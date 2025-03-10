import base64
from google.genai import types
from google import genai
import os
import json
from datetime import datetime
import random
from loguru import logger
from config import (
    bot, CHAT_ID, FOOD_FILE, ACTIVE_VOTE_FILE,
    COMPLETED_VOTE_FILE, DEFAULT_FOOD_LIST,
    GEMINI_API_KEY
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
                current_time = datetime.now().strftime("%H:%M")
                active_votes = load_active_votes()
                if 'today_foods' not in active_votes:
                    bot.reply_to(message, "Chưa có bữa ăn nào được chọn!")
                    return
                try:
                    amount = float(message.text.split()[1])
                except (IndexError, ValueError):
                    bot.reply_to(message, "Vui lòng nhập số tiền hợp lệ! Ví dụ: /debt 100000")
                    return
                # Lấy thông tin người trả tiền
                payer = message.from_user
                payer_name = f"{payer.first_name} {payer.last_name if payer.last_name else ''}".strip()
                # Lấy vote gần nhất từ completed_votes
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
                # Sắp xếp và hiển thị danh sách
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

    @bot.message_handler(commands=['ai'])
    def handle_ai_command(message):
        try:
            logger.info(f"Received AI command: {message.text}")

            # Trích xuất nội dung sau lệnh /ai
            command_parts = message.text.split(' ', 1)
            if len(command_parts) > 1:
                prompt = command_parts[1].strip()
                logger.info(f"Extracted prompt: {prompt}")

                if prompt:
                    bot.send_chat_action(message.chat.id, 'typing')
                    response = chat_with_gemini(prompt)
                    bot.reply_to(message, response)
                    logger.info("Response sent successfully")
                else:
                    bot.reply_to(message, "Vui lòng cung cấp nội dung sau lệnh /ai!")
            else:
                bot.reply_to(message, "Vui lòng cung cấp nội dung sau lệnh /ai!")

        except Exception as e:
            logger.error(f"Error in handle_ai_command: {str(e)}")
            bot.reply_to(message, "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn.")


@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    try:
        active_votes = load_active_votes()
        if 'food_poll' not in active_votes:
            return
        poll_data = active_votes['food_poll']
        if poll_answer.poll_id != poll_data['poll_id']:
            return
        user = poll_answer.user
        user_name = f"{user.first_name} {user.last_name if user.last_name else ''}"
        option_id = poll_answer.option_ids[0]
        if 'votes' not in poll_data:
            poll_data['votes'] = {}
        poll_data['votes'][user_name] = poll_data['options'][option_id]
        active_votes['food_poll'] = poll_data
        save_active_votes(active_votes)
        logger.bind(active_vote=True).info(f"Vote recorded: {user_name} voted for {poll_data['options'][option_id]}")
    except Exception as e:
        logger.error(f"Error handling poll answer: {str(e)}")


def create_food_poll():
    try:
        current_time = datetime.now().strftime("%H:%M")
        food_data = load_food_list()
        if len(food_data['foods']) > 8:
            selected_foods = random.sample(food_data['foods'], 8)
        else:
            selected_foods = food_data['foods']
        options = selected_foods + ['Nhịn', ]
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
            'votes': {},
            'created_at': datetime.now().isoformat()
        }
        save_active_votes(active_votes)
        logger.bind(active_vote=True).info(f"Created food poll at {current_time}")
    except Exception as e:
        logger.error(f"Error creating food poll: {str(e)}")


def close_food_poll():
    active_votes = load_active_votes()
    if 'food_poll' not in active_votes:
        logger.error("No active food poll to close")
        return
    poll_data = active_votes['food_poll']
    # Get poll results
    poll_message = bot.forward_message(CHAT_ID, CHAT_ID, poll_data['message_id'])
    poll = poll_message.poll
    if not poll:
        logger.error("Could not get poll results")
        bot.send_message(CHAT_ID, "❌ Không thể lấy kết quả poll!")
        return
    # Count votes
    vote_counts = {}
    voters = {}  # Track who voted for what
    total_voters = 0
    for i, option in enumerate(poll.options):
        vote_count = option.voter_count
        if vote_count > 0:
            option_text = poll_data['options'][i]
            vote_counts[option_text] = vote_count
            # Store voters for this option from poll_data votes
            voters[option_text] = [user for user, vote in poll_data['votes'].items()
                                   if vote == option_text]
            total_voters += vote_count
    # Select winning food
    regular_options = [opt for opt in poll_data['options']
                       if opt not in ['Nhịn', ]]
    if vote_counts:
        # Find option with most votes (excluding special options)
        regular_votes = {k: v for k, v in vote_counts.items()
                         if k in regular_options}
        if regular_votes:
            max_votes = max(regular_votes.values())
            max_voted = [food for food, count in regular_votes.items()
                         if count == max_votes]
            selected_food = max_voted[0]  # Take first option with max votes
        else:
            # Only if no regular options received votes
            selected_food = random.choice(regular_options)
    else:
        selected_food = random.choice(regular_options)
    # Store result with full datetime
    now = datetime.now()
    active_votes['today_foods'] = selected_food
    active_votes['vote_time'] = now.isoformat()
    active_votes['voters'] = voters  # Store who voted for what
    save_active_votes(active_votes)
    # Save to completed votes
    completed_votes = load_completed_votes()
    completed_votes[now.isoformat()] = {
        'type': 'food',
        'selected': selected_food,
        'poll_options': poll_data['options'],
        'vote_counts': vote_counts,
        'voters': voters
    }
    save_completed_votes(completed_votes)
    # Remove food poll but keep today's food and voters
    del active_votes['food_poll']
    save_active_votes(active_votes)
    # Send results
    vote_summary = f"📊 Kết quả vote [{now.strftime('%Y-%m-%d %H:%M')}]:\n"
    for food, count in vote_counts.items():
        percentage = (count / total_voters) * 100
        vote_summary += f"- {food}: {count} vote ({percentage:.1f}%)\n"
    bot.send_message(CHAT_ID, vote_summary)
    result_message = (
        f"🎉 Kết quả: Hôm nay chúng ta sẽ ăn {selected_food}!\n\n"
        "💰 Người thanh toán vui lòng dùng lệnh /debt [số tiền] để khai báo số tiền.\n"
        "Ví dụ: /debt 100000"
    )
    bot.send_message(CHAT_ID, result_message)


def chat_with_gemini(prompt):
    """Send prompt to Gemini and get response"""
    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY,
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=prompt
                    ),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
        )

        # Collect the response chunks
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text

        return response_text
    except Exception as e:
        logger.error(f"Error chatting with Gemini: {str(e)}")
        return "Sorry, I encountered an error while processing your request."
