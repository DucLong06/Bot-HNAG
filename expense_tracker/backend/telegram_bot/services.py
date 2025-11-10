import requests
import tempfile
import os
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
                grouped_by_payer[payer].append(participant)
                total_debt += participant.amount_owed

            overview_message = f"🔔 Nhắc nhở thanh toán\n\n"
            overview_message += f"Chào {member.name}!\n\n"
            overview_message += f"Bạn có {len(unpaid_participants)} khoản chưa thanh toán:\n"
            overview_message += f"💰 Tổng cộng: {total_debt:,.0f} VND\n\n"
            overview_message += f"Chi tiết thanh toán từng người 👇"

            success = self._send_text_message(member.telegram_id, overview_message)
            if not success:
                return False

            for payer, participants in grouped_by_payer.items():
                self._send_payer_details(member.telegram_id, member.name, payer, participants)

            return True

        except Exception as e:
            print(f"❌ [TELEGRAM SERVICE] Error: {e}")
            return False

    def _send_payer_details(self, chat_id, debtor_name, payer, participants):
        payer_total = sum(p.amount_owed for p in participants)

        message = f"💰 Thanh toán cho {payer.name}\n"
        message += f"Số tiền: {payer_total:,.0f} VND\n\n"

        if payer.bank_name and payer.account_number:
            message += f"🏦 Ngân hàng: {payer.bank_name}\n"
            message += f"💳 Số TK: {payer.account_number}\n"
            message += f"👤 Chủ TK: {payer.name}\n\n"
        else:
            message += f"⚠️ Chưa có thông tin STK, liên hệ {payer.name}\n\n"

        message += f"📝 Chi tiết các khoản:\n"
        for participant in participants:
            message += f"• {participant.expense.name}: {participant.amount_owed:,.0f} VND\n"

        expense_names = [p.expense.name for p in participants]
        description = f"{debtor_name} tra {payer.name}: {', '.join(expense_names[:2])}"
        if len(expense_names) > 2:
            description += f" va {len(expense_names)-2} mon khac"

        message += f"\n💬 Nội dung CK: {description}"

        self._send_text_message(chat_id, message)

        # if payer.bank_name and payer.account_number:
        #     self._send_qr_code(chat_id, payer, payer_total, f"{debtor_name} ck")

    def _send_qr_code(self, chat_id, payer, amount, description):
        try:
            qr_data = QRService.create_payment_qr_data(
                bank_name=payer.bank_name,
                account_number=payer.account_number,
                account_name=payer.name,
                amount=amount,
                description=description
            )

            qr_base64 = QRService.create_qr_image_base64(qr_data)
            if not qr_base64:
                return False

            import base64
            qr_image_data = base64.b64decode(qr_base64.split(',')[1])

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(qr_image_data)
                temp_file_path = temp_file.name

            success = self._send_photo_file(chat_id, temp_file_path, f"📱 QR thanh toán {payer.name}")

            os.unlink(temp_file_path)

            return success

        except Exception as e:
            print(f"Error creating/sending QR: {e}")
            return False

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
        except:
            return False

    def _send_photo_file(self, chat_id, file_path, caption=""):
        try:
            url = f"{self.base_url}/sendPhoto"

            with open(file_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data, timeout=15)
                return response.status_code == 200
        except Exception as e:
            print(f"Error sending photo file: {e}")
            return False
