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

        # Gửi ảnh QR nếu có, nếu không thì gửi text
        if qr_url:
            # Gửi kèm ảnh (Telegram tự tải ảnh từ URL)
            self._send_photo_url(chat_id, qr_url, message)
        else:
            message += "\n⚠️ <i>Chưa có thông tin ngân hàng để tạo QR</i>"
            self._send_text_message(chat_id, message)

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

    def _send_photo_url(self, chat_id, photo_url, caption=""):
        try:
            url = f"{self.base_url}/sendPhoto"
            payload = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=15)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending photo URL: {e}")
            return False
