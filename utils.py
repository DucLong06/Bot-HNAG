# utils.py
import json
from datetime import datetime
import random
from loguru import logger
from config import (
    bot, CHAT_ID, FOOD_FILE, ACTIVE_VOTE_FILE,
    COMPLETED_VOTE_FILE, DEFAULT_FOOD_LIST
)

# File operations


def load_food_list():
    try:
        with open(FOOD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        save_food_list(DEFAULT_FOOD_LIST)
        return DEFAULT_FOOD_LIST


def save_food_list(food_data):
    with open(FOOD_FILE, 'w', encoding='utf-8') as f:
        json.dump(food_data, f, ensure_ascii=False, indent=2)


def load_active_votes():
    try:
        with open(ACTIVE_VOTE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_completed_votes():
    try:
        with open(COMPLETED_VOTE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_active_votes(votes):
    with open(ACTIVE_VOTE_FILE, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)


def save_completed_votes(votes):
    with open(COMPLETED_VOTE_FILE, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)

# Bot command handlers


def bot_command_handlers():
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        help_text = """
    🤖 Xin chào! Bot hỗ trợ các tính năng sau:

    1️⃣ Gợi ý món ăn:
    /add [tên món] - Thêm món ăn mới
    /list - Xem danh sách món ăn
    /remove [tên món] - Xóa món ăn

    2️⃣ Tính tiền nhóm:
    /debt [số tiền] - Khai báo số tiền (dành cho người được chọn trả tiền)
    /pay [@user1 @user2]` - Thêm người vào danh sách chia tiền

    ⚠️ Các tính năng khác được chạy tự động theo lịch:
    - Tạo poll chọn món ăn
    - Đóng poll chọn món
        """
        bot.reply_to(message, help_text)
        logger.info(f"User {message.from_user.first_name} started bot")

    @bot.message_handler(commands=['add'])
    def add_food(message):
        try:
            food_name = ' '.join(message.text.split()[1:])
            if not food_name:
                bot.reply_to(message, "Vui lòng nhập tên món ăn! Ví dụ: /add Phở bò")
                return

            food_data = load_food_list()
            if food_name in food_data['foods']:
                bot.reply_to(message, f"Món {food_name} đã có trong danh sách!")
                return

            food_data['foods'].append(food_name)
            save_food_list(food_data)
            bot.reply_to(message, f"Đã thêm món {food_name} vào danh sách!")
            logger.info(f"Added food: {food_name} by {message.from_user.first_name}")
        except Exception as e:
            logger.error(f"Error adding food: {str(e)}")
            bot.reply_to(message, "Có lỗi xảy ra khi thêm món ăn!")

    @bot.message_handler(commands=['remove'])
    def remove_food(message):
        try:
            food_name = ' '.join(message.text.split()[1:])
            if not food_name:
                bot.reply_to(message, "Vui lòng nhập tên món ăn cần xóa! Ví dụ: /remove Phở bò")
                return

            food_data = load_food_list()
            if food_name not in food_data['foods']:
                bot.reply_to(message, f"Không tìm thấy món {food_name} trong danh sách!")
                return

            food_data['foods'].remove(food_name)
            save_food_list(food_data)
            bot.reply_to(message, f"Đã xóa món {food_name} khỏi danh sách!")
            logger.info(f"Removed food: {food_name} by {message.from_user.first_name}")
        except Exception as e:
            logger.error(f"Error removing food: {str(e)}")
            bot.reply_to(message, "Có lỗi xảy ra khi xóa món ăn!")

    @bot.message_handler(commands=['list'])
    def list_foods(message):
        try:
            food_data = load_food_list()
            food_list = "\n".join([f"- {food}" for food in food_data['foods']])
            response = f"📋 Danh sách món ăn:\n\n{food_list}"
            bot.reply_to(message, response)
            logger.info(f"Listed foods for {message.from_user.first_name}")
        except Exception as e:
            logger.error(f"Error listing foods: {str(e)}")
            bot.reply_to(message, "Có lỗi xảy ra khi hiển thị danh sách món ăn!")

    @bot.message_handler(commands=['debt'])
    def register_debt(message):
        try:
            now = datetime.now()
            active_votes = load_active_votes()

            if 'today_foods' not in active_votes or 'voters' not in active_votes:
                bot.reply_to(message, "Chưa có bữa ăn nào được chọn!")
                return

            try:
                amount = float(message.text.split()[1])
            except (IndexError, ValueError):
                bot.reply_to(message, "Vui lòng nhập số tiền hợp lệ! Ví dụ: /debt 100000")
                return

            # Get payer info
            payer = message.from_user
            payer_name = f"{payer.first_name} {payer.last_name if payer.last_name else ''}".strip()

            # Get participants excluding those who voted "Nhịn"
            all_voters = []
            for option, voters_list in active_votes['voters'].items():
                if option != 'Nhịn':  # Skip people who voted "Nhịn"
                    all_voters.extend(voters_list)

            # Add payer if they're not in the list
            participants = list(set(all_voters + [payer_name]))
            total_participants = len(participants)

            if total_participants == 0:
                bot.reply_to(message, "Không có người tham gia nào được ghi nhận!")
                return

            per_person = amount / total_participants

            # Get list of people who voted "Nhịn" for display
            skipped_participants = active_votes['voters'].get('Nhịn', [])

            # Prepare result message
            result = f"💰 Chi tiết chia tiền [{now.strftime('%Y-%m-%d %H:%M')}]:\n\n"
            result += f"🍽️ Món ăn: {active_votes['today_foods']}\n"
            result += f"💵 Tổng tiền: {amount:,.0f}đ\n"
            result += f"👥 Số người: {total_participants}\n"
            result += f"💰 Mỗi người: {per_person:,.0f}đ\n\n"
            result += "📋 Danh sách người cần đóng tiền:\n"

            # Sort and display list
            sorted_participants = sorted(participants)
            for idx, participant in enumerate(sorted_participants, 1):
                if participant == payer_name:
                    result += f"{idx}. {participant}: {per_person:,.0f}đ (Người trả)\n"
                else:
                    result += f"{idx}. {participant}: {per_person:,.0f}đ\n"

            # Add list of people who voted "Nhịn"
            if skipped_participants:
                result += "\n🚫 Những người không tham gia:\n"
                for idx, participant in enumerate(sorted(skipped_participants), 1):
                    result += f"{idx}. {participant}\n"

            result += "\n💡 Vui lòng chuyển khoản cho người trả tiền!"

            bot.send_message(CHAT_ID, result)

            # Save to completed votes with full datetime
            completed_votes = load_completed_votes()
            completed_votes[now.isoformat()] = {
                'type': 'payment',
                'datetime': now.isoformat(),
                'payer': payer_name,
                'amount': amount,
                'per_person': per_person,
                'food': active_votes['today_foods'],
                'total_participants': total_participants,
                'participants': sorted_participants,
                'skipped_participants': sorted(skipped_participants)  # Add list of people who skipped
            }
            save_completed_votes(completed_votes)

            # Clear active votes
            active_votes.clear()
            save_active_votes(active_votes)

            logger.info(
                f"Payment registered: {amount} by {payer_name}, "
                f"per person: {per_person}, total participants: {total_participants}, "
                f"skipped: {len(skipped_participants)}"
            )

        except Exception as e:
            logger.error(f"Error registering debt: {str(e)}")
            bot.reply_to(message, "Có lỗi xảy ra khi xử lý khai báo tiền!")
            try:
                current_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                active_votes = load_active_votes()
                if 'today_foods' not in active_votes:
                    bot.reply_to(message, "Chưa có bữa ăn nào được chọn!")
                    return

                try:
                    amount = float(message.text.split()[1])
                except (IndexError, ValueError):
                    bot.reply_to(message, "Vui lòng nhập số tiền hợp lệ! Ví dụ: /debt 100000")
                    return

                payer = message.from_user
                payer_name = f"{payer.first_name} {payer.last_name if payer.last_name else ''}".strip()

                completed_votes = load_completed_votes()
                if not completed_votes:
                    # Nếu không có vote nào trước đó, tạo danh sách chỉ với người trả tiền
                    total_participants = 1
                    participants = [payer_name]
                else:
                    latest_vote = max(completed_votes.items(), key=lambda x: x[0])
                    vote_data = latest_vote[1]
                    votes = vote_data.get('votes', {})

                    # Tạo danh sách người tham gia từ votes và người trả tiền
                    participants = list(set(list(votes.keys()) + [payer_name]))
                    total_participants = len(participants)

                per_person = amount / total_participants

                # Prepare result message
                result = f"💰 Chi tiết chia tiền [{current_time}]:\n\n"
                result += f"🍽️ Món ăn: {active_votes['today_foods']}\n"
                result += f"💵 Tổng tiền: {amount:,.0f}đ\n"
                result += f"👥 Số người: {total_participants}\n"
                result += f"💰 Mỗi người: {per_person:,.0f}đ\n\n"
                result += "📋 Danh sách người cần đóng tiền:\n"

                sorted_participants = sorted(participants)
                for idx, participant in enumerate(sorted_participants, 1):
                    if participant == payer_name:
                        result += f"{idx}. {participant}: {per_person:,.0f}đ (Người trả)\n"
                    else:
                        result += f"{idx}. {participant}: {per_person:,.0f}đ\n"

                result += "\n💡 Vui lòng chuyển khoản cho người trả tiền!"

                bot.send_message(CHAT_ID, result)

                # Save to completed votes
                completed_votes[datetime.now().isoformat()] = {
                    'type': 'payment',
                    'time': current_time,
                    'payer': payer_name,
                    'amount': amount,
                    'per_person': per_person,
                    'food': active_votes['today_foods'],
                    'total_participants': total_participants,
                    'participants': sorted_participants
                }
                save_completed_votes(completed_votes)

                # Clear active votes
                active_votes.clear()
                save_active_votes(active_votes)

                logger.bind(completed_vote=True).info(
                    f"Payment registered at {current_time}: {amount} by {payer_name}, "
                    f"per person: {per_person}, total participants: {total_participants}"
                )

            except Exception as e:
                logger.error(f"Error registering debt: {str(e)}")
                bot.reply_to(message, "Có lỗi xảy ra khi xử lý khai báo tiền!")

    @bot.message_handler(commands=['debt'])
    def register_debt(message):
        try:
            now = datetime.now()
            active_votes = load_active_votes()

            if 'today_foods' not in active_votes or 'participants' not in active_votes:
                bot.reply_to(message, "Chưa có bữa ăn nào được chọn hoặc danh sách người đi ăn trống!")
                return

            try:
                amount = float(message.text.split()[1])
            except (IndexError, ValueError):
                bot.reply_to(message, "Vui lòng nhập số tiền hợp lệ! Ví dụ: /debt 100000")
                return

            # Get payer info
            payer = message.from_user
            payer_name = f"{payer.first_name} {payer.last_name if payer.last_name else ''}".strip()

            # Add payer if they're not in the list
            if payer_name not in active_votes['participants']:
                active_votes['participants'].append(payer_name)

            total_participants = len(active_votes['participants'])
            per_person = amount / total_participants

            # Prepare result message
            result = f"💰 Chi tiết chia tiền [{now.strftime('%Y-%m-%d %H:%M')}]:\n\n"
            result += f"🍽️ Món ăn: {active_votes['today_foods']}\n"
            result += f"💵 Tổng tiền: {amount:,.0f}đ\n"
            result += f"👥 Số người: {total_participants}\n"
            result += f"💰 Mỗi người: {per_person:,.0f}đ\n\n"
            result += "📋 Danh sách người cần đóng tiền:\n"

            # Sort and display list
            sorted_participants = sorted(active_votes['participants'])
            for idx, participant in enumerate(sorted_participants, 1):
                if participant == payer_name:
                    result += f"{idx}. {participant}: {per_person:,.0f}đ (Người trả)\n"
                else:
                    result += f"{idx}. {participant}: {per_person:,.0f}đ\n"

            # Display skipped participants
            if active_votes.get('skipped'):
                result += "\n🚫 Những người không tham gia:\n"
                for idx, person in enumerate(sorted(active_votes['skipped']), 1):
                    result += f"{idx}. {person}\n"

            result += "\n💡 Vui lòng chuyển khoản cho người trả tiền!"

            bot.send_message(CHAT_ID, result)

            # Save to completed votes
            completed_votes = load_completed_votes()
            completed_votes[now.isoformat()] = {
                'type': 'payment',
                'datetime': now.isoformat(),
                'payer': payer_name,
                'amount': amount,
                'per_person': per_person,
                'food': active_votes['today_foods'],
                'total_participants': total_participants,
                'participants': sorted_participants,
                'skipped': sorted(active_votes.get('skipped', []))
            }
            save_completed_votes(completed_votes)

            # Clear active votes
            active_votes.clear()
            save_active_votes(active_votes)

            logger.info(
                f"Payment registered: {amount} by {payer_name}, "
                f"per person: {per_person}, total participants: {total_participants}"
            )

        except Exception as e:
            logger.error(f"Error registering debt: {str(e)}")
            bot.reply_to(message, "Có lỗi xảy ra khi xử lý khai báo tiền!")

    @bot.message_handler(commands=['unpay'])
    def remove_payment_participants(message):
        try:
            if not message.entities or len(message.entities) < 2:
                bot.reply_to(message, "Vui lòng tag người cần xóa khỏi danh sách! Ví dụ: /unpay @user1 @user2")
                return

            active_votes = load_active_votes()
            if 'participants' not in active_votes:
                bot.reply_to(message, "Chưa có danh sách người đi ăn nào được tạo!")
                return

            # Process mentioned users
            removed_users = []
            for entity in message.entities[1:]:
                if entity.type == 'mention':
                    username = message.text[entity.offset:entity.offset + entity.length]
                    if username in active_votes['participants']:
                        active_votes['participants'].remove(username)
                        # Add to skipped list if not already there
                        if 'skipped' not in active_votes:
                            active_votes['skipped'] = []
                        if username not in active_votes['skipped']:
                            active_votes['skipped'].append(username)
                        removed_users.append(username)

            if removed_users:
                save_active_votes(active_votes)
                # Show updated lists
                response = "📋 Danh sách đã được cập nhật:\n\n"
                response += "👥 Người đi ăn:\n"
                for idx, participant in enumerate(sorted(active_votes['participants']), 1):
                    response += f"{idx}. {participant}\n"

                if active_votes.get('skipped'):
                    response += "\n🚫 Người không tham gia:\n"
                    for idx, person in enumerate(sorted(active_votes['skipped']), 1):
                        response += f"{idx}. {person}\n"

                bot.reply_to(message, response)
                logger.info(f"Removed payment participants: {removed_users}")
            else:
                bot.reply_to(message, "❌ Không có người dùng nào được xóa khỏi danh sách!")

        except Exception as e:
            logger.error(f"Error removing payment participants: {str(e)}")
            bot.reply_to(message, "Có lỗi xảy ra khi xóa người khỏi danh sách!")


def create_food_poll():
    try:
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        food_data = load_food_list()
        if len(food_data['foods']) > 9:
            selected_foods = random.sample(food_data['foods'], 9)
        else:
            selected_foods = food_data['foods']

        options = selected_foods + ['Nhịn']
        poll = bot.send_poll(
            CHAT_ID,
            f"🍽️ [{current_time}] Hôm nay ăn gì?",
            options,
            is_anonymous=False,
            allows_multiple_answers=False
        )

        active_votes = load_active_votes()
        active_votes['food_poll'] = {
            'poll_id': poll.poll.id,
            'message_id': poll.message_id,
            'options': options,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        save_active_votes(active_votes)
        logger.bind(active_vote=True).info(f"Created food poll at {current_time}")

    except Exception as e:
        logger.error(f"Error creating food poll: {str(e)}")
        bot.send_message(CHAT_ID, "❌ Có lỗi xảy ra khi tạo poll!")


def close_food_poll():
    try:
        active_votes = load_active_votes()
        if ('food_poll' not in active_votes or
                active_votes['food_poll'].get('status') != 'active'):
            logger.error("No active food poll to close")
            return

        poll_data = active_votes['food_poll']
        poll_message = bot.forward_message(CHAT_ID, CHAT_ID, poll_data['message_id'])
        poll = poll_message.poll

        if not poll:
            logger.error("Could not get poll results")
            bot.send_message(CHAT_ID, "❌ Không thể lấy kết quả poll!")
            return

        vote_counts = {}
        voters = {}  # Track who voted for what
        total_voters = 0
        participants = []  # List of people going to eat
        skipped = []      # List of people who voted "Nhịn"

        for i, option in enumerate(poll.options):
            option_text = poll_data['options'][i]
            if hasattr(option, 'voter_list'):
                voters_for_option = []
                for voter in option.voter_list:
                    voter_name = f"{voter.first_name} {voter.last_name if voter.last_name else ''}".strip()
                    voters_for_option.append(voter_name)
                if voters_for_option:
                    voters[option_text] = voters_for_option
                    vote_counts[option_text] = len(voters_for_option)
                    total_voters += len(voters_for_option)

                    # Sort voters into participants and skipped
                    if option_text == 'Nhịn':
                        skipped.extend(voters_for_option)
                    else:
                        participants.extend(voters_for_option)

        # Select winning food
        regular_options = [opt for opt in poll_data['options'] if opt != 'Nhịn']

        if vote_counts:
            regular_votes = {k: v for k, v in vote_counts.items() if k in regular_options}
            if regular_votes:
                max_votes = max(regular_votes.values())
                max_voted = [food for food, count in regular_votes.items() if count == max_votes]
                selected_food = random.choice(max_voted)  # Random if multiple max
            else:
                selected_food = random.choice(regular_options)
        else:
            selected_food = random.choice(regular_options)

        now = datetime.now()

        # Update active_votes with participant information
        active_votes.update({
            'today_foods': selected_food,
            'vote_time': now.isoformat(),
            'participants': participants,
            'skipped': skipped,
            'voters': voters
        })
        save_active_votes(active_votes)

        # Save to completed_votes
        completed_votes = load_completed_votes()
        completed_votes[now.isoformat()] = {
            'type': 'food',
            'selected': selected_food,
            'poll_options': poll_data['options'],
            'vote_counts': vote_counts,
            'voters': voters,
            'participants': participants,
            'skipped': skipped,
            'poll_id': poll_data['poll_id'],
            'message_id': poll_data['message_id']
        }
        save_completed_votes(completed_votes)

        # Display vote summary
        vote_summary = f"📊 Kết quả vote [{now.strftime('%d/%m/%Y, %H:%M:%S')}]:\n\n"
        vote_summary += f"🍽️ Món được chọn: {selected_food}\n\n"

        # Display participants
        vote_summary += "👥 Danh sách người đi ăn:\n"
        for idx, participant in enumerate(sorted(participants), 1):
            vote_summary += f"{idx}. {participant}\n"

        # Display people who skipped
        if skipped:
            vote_summary += "\n🚫 Những người không tham gia:\n"
            for idx, person in enumerate(sorted(skipped), 1):
                vote_summary += f"{idx}. {person}\n"

        vote_summary += "\n✏️ Để chỉnh sửa danh sách:\n"
        vote_summary += "- Thêm người: /pay @tênngười\n"
        vote_summary += "- Xóa người: /unpay @tênngười\n\n"
        vote_summary += "💰 Sau khi chỉnh sửa xong, người thanh toán vui lòng dùng lệnh /debt [số tiền] để khai báo số tiền."

        bot.send_message(CHAT_ID, vote_summary)

        logger.info(
            f"Poll closed successfully. Selected food: {selected_food}, "
            f"Participants: {len(participants)}, Skipped: {len(skipped)}"
        )

    except Exception as e:
        logger.error(f"Error closing food poll: {str(e)}")
        bot.send_message(CHAT_ID, "❌ Có lỗi xảy ra khi đóng poll!")
