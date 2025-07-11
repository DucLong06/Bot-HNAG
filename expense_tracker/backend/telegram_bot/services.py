import requests
from django.conf import settings
from members.models import Member
from expenses.models import ExpenseParticipant


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_debt_reminder(self, member_id):
        """Send debt reminder using requests (sync)"""
        try:
            member = Member.objects.get(id=member_id)
            unpaid_participants = ExpenseParticipant.objects.filter(
                member=member,
                is_paid=False
            ).select_related('expense')

            if not unpaid_participants:
                return False

            total_debt = sum(p.amount_owed for p in unpaid_participants)

            message = f"🔔 Nhắc nhở thanh toán\n\n"
            message += f"Chào {member.name}!\n\n"
            message += f"Bạn có {len(unpaid_participants)} khoản chưa thanh toán:\n\n"

            for participant in unpaid_participants:
                message += f"• {participant.expense.name}: {participant.amount_owed:,.0f} VND\n"

            message += f"\n💰 Tổng cộng: {total_debt:,.0f} VND"
            message += f"\n📅 Vui lòng thanh toán sớm nhất có thể!"

            # Send message using requests
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': member.telegram_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                return result.get('ok', False)
            else:
                print(f"Telegram API error: {response.status_code} - {response.text}")
                return False

        except Member.DoesNotExist:
            print(f"Member with id {member_id} not found")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Network error sending message: {e}")
            return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
