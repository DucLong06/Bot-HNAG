from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from telegram_bot.services import TelegramService
from telegram_bot.models import PaymentConfirmation
from members.models import Member
from expenses.models import ExpenseParticipant


class PaymentCallbackHandler:
    """
    Handles payment confirmation workflow callback queries.
    Routes callback_data to appropriate handlers.
    """

    def __init__(self):
        self.telegram_service = TelegramService()

    def handle_callback_query(self, callback_query):
        """
        Main entry point for processing callback queries.

        Args:
            callback_query: Telegram callback_query object from update

        Returns:
            bool: Success status
        """
        callback_id = callback_query["id"]
        data = callback_query["data"]  # e.g., "initiate_payment:1:2"
        user = callback_query["from"]
        user_telegram_id = str(user["id"])

        try:
            # CRITICAL: Answer callback immediately to remove spinner
            self.telegram_service.answer_callback_query(callback_id)

            # Route to appropriate handler
            if data.startswith("initiate_payment:"):
                parts = data.split(":")
                debtor_id, lender_id = int(parts[1]), int(parts[2])
                return self._handle_initiate_payment(
                    callback_query, user_telegram_id, debtor_id, lender_id
                )

            elif data.startswith("confirm_payment:"):
                confirmation_id = int(data.split(":")[1])
                return self._handle_confirm_payment(
                    callback_query, user_telegram_id, confirmation_id
                )

            elif data.startswith("reject_payment:"):
                confirmation_id = int(data.split(":")[1])
                return self._handle_reject_payment(
                    callback_query, user_telegram_id, confirmation_id
                )

            else:
                print(f"⚠️ Unknown callback data: {data}")
                return False

        except Exception as e:
            print(f"❌ [CALLBACK HANDLER] Error: {e}")
            # Send error notification to user
            try:
                chat_id = callback_query["message"]["chat"]["id"]
                self.telegram_service._send_text_message(
                    chat_id,
                    "⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau."
                )
            except:
                pass  # Best effort
            return False

    def _handle_initiate_payment(self, callback_query, user_telegram_id, debtor_id, lender_id):
        """
        Handle payment initiation from either debtor or lender.

        Creates PaymentConfirmation record and sends request to counterparty.
        """
        try:
            # Verify user authorization (must be debtor or lender)
            debtor = Member.objects.get(id=debtor_id)
            lender = Member.objects.get(id=lender_id)

            if user_telegram_id not in [debtor.telegram_id, lender.telegram_id]:
                self.telegram_service._send_text_message(
                    callback_query["message"]["chat"]["id"],
                    "❌ Bạn không có quyền thực hiện thao tác này."
                )
                return False

            # Determine who initiated (debtor or lender)
            initiator = debtor if user_telegram_id == debtor.telegram_id else lender

            # Calculate total unpaid amount between debtor-lender pair
            unpaid_participants = ExpenseParticipant.objects.filter(
                member=debtor,
                expense__payer=lender,
                is_paid=False
            ).select_related('expense')

            if not unpaid_participants.exists():
                self.telegram_service._send_text_message(
                    callback_query["message"]["chat"]["id"],
                    "✅ Không có khoản nợ nào giữa hai bên."
                )
                return False

            from decimal import Decimal
            total_amount = sum(
                (p.amount_owed for p in unpaid_participants),
                start=Decimal('0')
            )

            # Validate amount
            if total_amount <= 0:
                print(f"❌ Invalid total_amount: {total_amount} for debtor={debtor.id}, lender={lender.id}")
                self.telegram_service._send_text_message(
                    callback_query["message"]["chat"]["id"],
                    "❌ Số tiền không hợp lệ."
                )
                return False

            # Create PaymentConfirmation record with race condition protection
            created = False
            with transaction.atomic():
                # Check for existing pending confirmation inside transaction with lock
                existing = PaymentConfirmation.objects.select_for_update().filter(
                    debtor=debtor,
                    lender=lender,
                    status='pending'
                ).exists()

                if not existing:
                    confirmation = PaymentConfirmation.objects.create(
                        debtor=debtor,
                        lender=lender,
                        total_amount=total_amount,
                        initiated_by=initiator,
                        status='pending'
                    )
                    # Link expense participants
                    confirmation.expense_participants.set(unpaid_participants)
                    created = True

            # Send feedback outside transaction
            if not created:
                self.telegram_service._send_text_message(
                    callback_query["message"]["chat"]["id"],
                    "⚠️ Yêu cầu xác nhận thanh toán đã tồn tại."
                )
                return False

            # Send confirmation request to counterparty
            self._send_confirmation_request(confirmation)

            # Notify initiator
            counterparty_name = confirmation.counterparty.name
            self.telegram_service._send_text_message(
                callback_query["message"]["chat"]["id"],
                f"✅ Đã gửi yêu cầu xác nhận đến {counterparty_name}"
            )

            return True

        except Member.DoesNotExist:
            print(f"❌ Member not found: debtor={debtor_id}, lender={lender_id}")
            return False
        except Exception as e:
            print(f"❌ Error in initiate_payment: {e}")
            return False

    def _send_confirmation_request(self, confirmation):
        """
        Send confirmation request message with inline buttons to counterparty.

        Stores message_id for later editing.
        """
        counterparty = confirmation.counterparty
        initiator_name = confirmation.initiated_by.name

        # Build expense list
        expense_names = list(
            confirmation.expense_participants.values_list('expense__name', flat=True)
        )
        expense_list = ', '.join(expense_names[:3])  # Limit to 3 for readability
        if len(expense_names) > 3:
            expense_list += f" (+{len(expense_names) - 3} khoản khác)"

        # Create message text
        message = f"💰 <b>XÁC NHẬN THANH TOÁN</b>\n\n"
        message += f"{initiator_name} cho biết đã trả bạn <b>{confirmation.total_amount:,.0f} đ</b>\n"
        message += f"📝 Khoản: {expense_list}\n\n"
        message += "Bạn đã nhận được tiền chưa?"

        # Create inline keyboard
        keyboard = [[
            {"text": "✅ Đã nhận", "callback_data": f"confirm_payment:{confirmation.id}"},
            {"text": "❌ Chưa nhận", "callback_data": f"reject_payment:{confirmation.id}"}
        ]]

        # Send message
        result = self.telegram_service.send_message_with_keyboard(
            chat_id=counterparty.telegram_id,
            text=message,
            inline_keyboard=keyboard
        )

        # Store message_id for editing later
        if result:
            confirmation.confirmation_message_id = str(result["message_id"])
            confirmation.save(update_fields=['confirmation_message_id'])
            return True

        return False

    def _handle_confirm_payment(self, callback_query, user_telegram_id, confirmation_id):
        """
        Process payment confirmation.

        Updates all linked ExpenseParticipants, notifies both parties.
        """
        try:
            # Use atomic transaction with select_for_update to prevent race conditions
            with transaction.atomic():
                confirmation = PaymentConfirmation.objects.select_for_update().select_related(
                    'debtor', 'lender', 'initiated_by'
                ).prefetch_related('expense_participants').get(id=confirmation_id)

                # Authorization: Only counterparty can confirm
                counterparty = confirmation.counterparty
                if user_telegram_id != counterparty.telegram_id:
                    # Don't send message inside transaction
                    should_send_auth_error = True
                else:
                    should_send_auth_error = False

                # Check status (prevent double-confirmation)
                if confirmation.status != 'pending':
                    should_send_status_error = True
                    status_display = confirmation.get_status_display()
                else:
                    should_send_status_error = False

                # Only update if authorized and pending
                if not should_send_auth_error and not should_send_status_error:
                    # Mark all expense participants as paid
                    confirmation.expense_participants.update(is_paid=True)

                    # Update confirmation status
                    confirmation.status = 'confirmed'
                    confirmation.confirmed_at = timezone.now()
                    confirmation.save(update_fields=['status', 'confirmed_at'])
                    success = True
                else:
                    success = False

            # Send error messages outside transaction
            if should_send_auth_error:
                self.telegram_service._send_text_message(
                    callback_query["message"]["chat"]["id"],
                    "❌ Bạn không có quyền thực hiện thao tác này."
                )
                return False

            if should_send_status_error:
                self.telegram_service._send_text_message(
                    callback_query["message"]["chat"]["id"],
                    f"⚠️ Yêu cầu này đã được xử lý ({status_display})."
                )
                return False

            # Send notifications outside transaction
            if success:
                self._edit_confirmation_message_confirmed(confirmation)
                self._notify_payment_success(confirmation)

            return success

        except PaymentConfirmation.DoesNotExist:
            print(f"❌ PaymentConfirmation {confirmation_id} not found")
            return False
        except Exception as e:
            print(f"❌ Error in confirm_payment: {e}")
            return False

    def _edit_confirmation_message_confirmed(self, confirmation):
        """Edit original confirmation message to show confirmed status"""
        if not confirmation.confirmation_message_id:
            return  # Skip if message_id not stored

        new_text = f"✅ <b>THANH TOÁN ĐÃ XÁC NHẬN</b>\n\n"
        new_text += f"Khoản {confirmation.total_amount:,.0f} đ từ {confirmation.debtor.name}\n"
        new_text += f"Trạng thái: Đã hoàn tất ✅"

        self.telegram_service.edit_message_text(
            chat_id=confirmation.counterparty.telegram_id,
            message_id=confirmation.confirmation_message_id,
            new_text=new_text,
            reply_markup=None  # Remove buttons
        )

    def _notify_payment_success(self, confirmation):
        """
        Notify both debtor and lender after successful confirmation.
        """
        debtor = confirmation.debtor
        lender = confirmation.lender
        amount = confirmation.total_amount

        # Notify debtor
        debtor_message = f"✅ <b>THANH TOÁN ĐÃ XÁC NHẬN</b>\n\n"
        debtor_message += f"Khoản trả {lender.name}: <b>{amount:,.0f} đ</b>\n"
        debtor_message += "Trạng thái: Đã hoàn tất ✅\n\n"

        # Check remaining debts to this lender
        remaining_debt = ExpenseParticipant.objects.filter(
            member=debtor,
            expense__payer=lender,
            is_paid=False
        ).aggregate(total=Sum('amount_owed'))['total'] or 0

        if remaining_debt > 0:
            debtor_message += f"⚠️ Bạn vẫn còn nợ {lender.name}: {remaining_debt:,.0f} đ"
        else:
            debtor_message += f"🎉 Bạn đã thanh toán xong cho {lender.name}!"

        self.telegram_service._send_text_message(debtor.telegram_id, debtor_message)

        # Notify lender
        lender_message = f"✅ <b>THANH TOÁN ĐÃ GHI NHẬN</b>\n\n"
        lender_message += f"Nhận từ {debtor.name}: <b>{amount:,.0f} đ</b>\n"
        lender_message += "Trạng thái: Đã xác nhận ✅"

        self.telegram_service._send_text_message(lender.telegram_id, lender_message)

    def _handle_reject_payment(self, callback_query, user_telegram_id, confirmation_id):
        """
        Process payment rejection.

        Updates status, notifies initiator.
        """
        try:
            confirmation = PaymentConfirmation.objects.select_related(
                'debtor', 'lender', 'initiated_by'
            ).get(id=confirmation_id)

            # Authorization: Only counterparty can reject
            counterparty = confirmation.counterparty
            if user_telegram_id != counterparty.telegram_id:
                return False

            # Check status
            if confirmation.status != 'pending':
                return False

            # Update status
            confirmation.status = 'rejected'
            confirmation.save(update_fields=['status'])

            # Edit original message
            new_text = f"❌ <b>THANH TOÁN BỊ TỪ CHỐI</b>\n\n"
            new_text += f"Khoản {confirmation.total_amount:,.0f} đ từ {confirmation.debtor.name}\n"
            new_text += "Trạng thái: Đã từ chối ❌"

            self.telegram_service.edit_message_text(
                chat_id=counterparty.telegram_id,
                message_id=confirmation.confirmation_message_id,
                new_text=new_text,
                reply_markup=None
            )

            # Notify initiator
            initiator_message = f"❌ <b>YÊU CẦU BỊ TỪ CHỐI</b>\n\n"
            initiator_message += f"{counterparty.name} cho biết chưa nhận được {confirmation.total_amount:,.0f} đ\n\n"
            initiator_message += "Vui lòng kiểm tra lại hoặc liên hệ trực tiếp."

            self.telegram_service._send_text_message(
                confirmation.initiated_by.telegram_id,
                initiator_message
            )

            return True

        except PaymentConfirmation.DoesNotExist:
            return False
        except Exception as e:
            print(f"❌ Error in reject_payment: {e}")
            return False
