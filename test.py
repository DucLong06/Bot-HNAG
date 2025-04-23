import requests
import config

def send_poem_to_telegram(bot_token, chat_id):
    """
    Gửi bài thơ vào group Telegram

    Args:
        bot_token (str): Token của Telegram bot
        chat_id (str): ID của group chat
    """

    poem = """Em trai Đức Thiện của Trung Béo đói rồi. Mọi người đi ăn thôi!!!
"""

    # API endpoint của Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Tạo payload
    payload = {
        "chat_id": chat_id,
        "text": poem,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("send success!")
        else:
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")


bot_token = config.BOT_TOKEN
chat_id = config.CHAT_ID
send_poem_to_telegram(bot_token, chat_id)
# def get_curl_command(bot_token, chat_id):
#     poem_escaped = poem.replace('"', '\\"').replace('\n', '\\n')
#     curl_command = f'''curl -X POST \\
#     https://api.telegram.org/bot{bot_token}/sendMessage \\
#     -H "Content-Type: application/json" \\
#     -d '{{"chat_id": "{chat_id}", "text": "{poem_escaped}", "parse_mode": "HTML"}}'
#     '''
#     return curl_command
