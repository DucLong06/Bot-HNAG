import requests
from django.conf import settings
from members.models import Member
from expenses.models import ExpenseParticipant
from collections import defaultdict
from utils.qr_service import QRService


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_debt_reminder(self, member_id):
        """Send debt reminder with QR codes"""
        try:
            member = Member.objects.get(id=member_id)
            # Tối ưu N+1 query
            unpaid_participants = ExpenseParticipant.objects.filter(
                member=member,
                is_paid=False
            ).select_related('expense', 'expense__payer')

            if not unpaid_participants:
                return False

            grouped_by_payer = defaultdict(list)
            total_debt = 0

            for participant in unpaid_participants:
                payer = participant.expense.payer
                # Bỏ qua nếu tự nợ chính mình
                if payer.id == member.id:
                    continue

                grouped_by_payer[payer].append(participant)
                total_debt += participant.amount_owed

            if total_debt == 0:
                return False

            # Khởi tạo debtor_name an toàn
            debtor_name = member.name or "Người nợ"

            # Gửi tin nhắn tổng quan
            overview_message = f"🔔 <b>NHẮC THANH TOÁN</b>\n"
            overview_message += f"Chào {debtor_name}!\n"
            overview_message += f"Bạn đang nợ tổng cộng: <b>{total_debt:,.0f} đ</b>\n"
            overview_message += f"Chi tiết bên dưới 👇"

            self._send_text_message(member.telegram_id, overview_message)

            # Gửi chi tiết từng chủ nợ kèm QR
            for payer, participants in grouped_by_payer.items():
                self._send_payer_details_with_qr(member.telegram_id, debtor_name, payer, participants)

            return True

        except Member.DoesNotExist:
            print(f"❌ [TELEGRAM SERVICE] Error: Member with ID {member_id} not found.")
            return False
        except Exception as e:
            # Lỗi "string index out of range" sẽ được catch ở đây
            print(f"❌ [TELEGRAM SERVICE] Error: {e}")
            return False

    def _send_payer_details_with_qr(self, chat_id, debtor_name, payer, participants):
        payer_total = sum(p.amount_owed for p in participants)

        # Safeguard names from being empty/None
        safe_debtor_name = debtor_name or "Người nợ"
        safe_payer_name = payer.name or "Chủ nợ"

        # Tạo nội dung tin nhắn
        message = f"👤 <b>Trả cho: {safe_payer_name}</b>\n"
        message += f"💰 Số tiền: <b>{payer_total:,.0f} đ</b>\n"

        # Chi tiết các món
        expense_names = [p.expense.name for p in participants]
        message += f"📝 Khoản chi: {', '.join(expense_names)}\n"

        # Tạo nội dung chuyển khoản: "TenTra no TenNhan"
        description = f"{safe_debtor_name} tra {safe_payer_name}"

        # Tạo link QR
        qr_url = None
        if payer.bank_name and payer.account_number:
            qr_url = QRService.get_vietqr_url(
                bank_name=payer.bank_name,
                account_number=payer.account_number,
                amount=payer_total,
                description=description,
                account_name=payer.name
            )
            message += f"🏦 {payer.bank_name} - {payer.account_number}"

        # Create inline keyboard with payment confirmation button
        debtor_id = participants[0].member.id  # Get debtor ID from first participant

        # Validate IDs before creating callback_data
        if not isinstance(debtor_id, int) or not isinstance(payer.id, int):
            print(f"⚠️ [TELEGRAM] Invalid ID types: debtor={type(debtor_id)}, payer={type(payer.id)}")
            # Fallback: send message without button
            if qr_url:
                self._send_photo_url(chat_id, qr_url, message)
            else:
                message += "\n⚠️ <i>Chưa có thông tin ngân hàng để tạo QR</i>"
                self._send_text_message(chat_id, message)
            return

        # SECURITY NOTE: callback_data contains debtor_id and payer_id
        # Phase 02 handler MUST validate that callback_query.from.id matches debtor.telegram_id
        # to prevent impersonation attacks
        callback_data = f"initiate_payment:{debtor_id}:{payer.id}"

        # Validate callback_data length (Telegram limit: 64 bytes)
        if len(callback_data.encode('utf-8')) > 64:
            print(f"⚠️ [TELEGRAM] Callback data exceeds 64 bytes: {len(callback_data)} bytes")
            # Fallback: send message without button
            if qr_url:
                self._send_photo_url(chat_id, qr_url, message)
            else:
                message += "\n⚠️ <i>Chưa có thông tin ngân hàng để tạo QR</i>"
                self._send_text_message(chat_id, message)
            return

        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "✅ Tôi đã trả tiền này",
                    "callback_data": callback_data
                }
            ]]
        }

        # Gửi ảnh QR nếu có, nếu không thì gửi text
        if qr_url:
            # Gửi kèm ảnh (Telegram tự tải ảnh từ URL) với inline button
            self._send_photo_url(chat_id, qr_url, message, reply_markup=keyboard)
        else:
            message += "\n⚠️ <i>Chưa có thông tin ngân hàng để tạo QR</i>"
            # Send message with keyboard even without QR code
            self._send_text_message_with_keyboard(chat_id, message, keyboard)

    def _send_text_message(self, chat_id, message):
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending text: {e}")
            return False

    def _send_photo_url(self, chat_id, photo_url, caption="", reply_markup=None):
        try:
            url = f"{self.base_url}/sendPhoto"
            payload = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': 'HTML'
            }

            # Add reply_markup if provided (for inline keyboards)
            if reply_markup:
                payload['reply_markup'] = reply_markup

            response = requests.post(url, json=payload, timeout=15)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending photo URL: {e}")
            return False

    def get_telegram_updates(self, timeout=30):
        """
        Poll Telegram API for new updates.
        Uses stored offset to prevent duplicate processing.

        WARNING: Only ONE instance of polling loop should run at a time.
        Use cron locking mechanism or ensure single process to prevent race conditions.

        Args:
            timeout: Long polling timeout in seconds (default: 30)

        Returns:
            list: Update objects from Telegram API
        """
        from telegram_bot.models import TelegramUpdateOffset
        from django.db import transaction

        # Fetch current offset (quick transaction)
        with transaction.atomic():
            offset_obj = TelegramUpdateOffset.objects.select_for_update().get_or_create(pk=1)[0]
            current_offset = offset_obj.offset

        # HTTP request outside transaction to avoid holding DB lock
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.post(
                url,
                json={"offset": current_offset + 1, "timeout": timeout},
                timeout=timeout + 5  # Add 5s buffer
            )

            if response.status_code == 200:
                data = response.json()
                updates = data.get("result", [])

                # Update offset in separate transaction after successful fetch
                if updates:
                    max_update_id = max(u["update_id"] for u in updates)
                    with transaction.atomic():
                        offset_obj = TelegramUpdateOffset.objects.select_for_update().get_or_create(pk=1)[0]
                        # Only update if no newer offset written (handle concurrent updates)
                        if max_update_id > offset_obj.offset:
                            offset_obj.offset = max_update_id
                            offset_obj.save()

                return updates
            else:
                error_code = response.json().get("error_code", "unknown") if response.text else "unknown"
                print(f"❌ [TELEGRAM] getUpdates failed: code={error_code}")
                return []

        except requests.Timeout:
            # Normal for long polling - return empty
            return []
        except Exception as e:
            print(f"❌ [TELEGRAM] Error polling updates: {type(e).__name__}")
            return []

    def send_message_with_keyboard(self, chat_id, text, inline_keyboard):
        """
        Send message with inline keyboard buttons.

        Args:
            chat_id: Telegram chat ID
            text: Message text (supports HTML)
            inline_keyboard: List of button rows, e.g.,
                [[{"text": "✅ Confirm", "callback_data": "confirm_123"}]]

        Returns:
            dict: Response containing message_id if successful, else None
        """
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": {"inline_keyboard": inline_keyboard}
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                return response.json().get("result")
            else:
                # Sanitize error message to prevent token/data leakage
                try:
                    error_data = response.json()
                    error_code = error_data.get("error_code", "unknown")
                    error_desc = error_data.get("description", "")[:50]  # Truncate
                    print(f"❌ [TELEGRAM] Send keyboard failed: code={error_code}, desc={error_desc}")
                except:
                    print(f"❌ [TELEGRAM] Send keyboard failed: status={response.status_code}")
                return None

        except Exception as e:
            print(f"❌ [TELEGRAM] Error sending keyboard: {type(e).__name__}")
            return None

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        """
        Answer callback query to remove loading spinner.
        MUST be called after receiving callback_query.

        Args:
            callback_query_id: ID from callback_query object
            text: Optional notification text (appears as toast or alert)
            show_alert: If True, shows alert popup instead of toast

        Returns:
            bool: Success status
        """
        url = f"{self.base_url}/answerCallbackQuery"

        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
            payload["show_alert"] = show_alert

        try:
            # Increased timeout to 10s for poor network conditions
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ [TELEGRAM] Error answering callback: {type(e).__name__}")
            return False

    def edit_message_text(self, chat_id, message_id, new_text, reply_markup=None):
        """
        Edit existing message text and buttons.

        Args:
            chat_id: Telegram chat ID
            message_id: ID of message to edit
            new_text: New message text
            reply_markup: New inline_keyboard (use None to remove buttons)

        Returns:
            bool: Success status
        """
        url = f"{self.base_url}/editMessageText"

        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "HTML"
        }

        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                return True
            else:
                # Non-critical error (message might be deleted by user)
                # Sanitize error message
                try:
                    error_data = response.json()
                    error_desc = error_data.get("description", "")[:50]
                    print(f"⚠️ [TELEGRAM] Edit failed (non-critical): {error_desc}")
                except:
                    print(f"⚠️ [TELEGRAM] Edit failed: status={response.status_code}")
                return False

        except Exception as e:
            print(f"⚠️ [TELEGRAM] Error editing message: {type(e).__name__}")
            return False

    def _send_text_message_with_keyboard(self, chat_id, message, keyboard):
        """
        Send text message with inline keyboard.
        Used when QR code not available but still want to show button.

        Args:
            chat_id: Telegram chat ID
            message: Message text (supports HTML)
            keyboard: Inline keyboard dict (same format as send_message_with_keyboard)

        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'reply_markup': keyboard
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending text with keyboard: {e}")
            return False
