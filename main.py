# main.py
import argparse
import os
from loguru import logger
from config import initialize_logger, bot, CHAT_ID
from utils import (
    create_food_poll,
    close_food_poll,
    bot_command_handlers
)


def main():
    parser = argparse.ArgumentParser(description='Bot Telegram quản lý ăn uống')
    parser.add_argument('--vote', action='store_true', help='Tạo poll chọn món ăn')
    parser.add_argument('--close-vote', action='store_true', help='Đóng poll chọn món ăn')
    parser.add_argument('--run', action='store_true', help='Chạy bot trong chế độ thường')

    args = parser.parse_args()

    try:
        if args.vote:
            create_food_poll()
            logger.info("Created food poll")
        elif args.close_vote:
            close_food_poll()
            logger.info("Closed food poll")
        elif args.run:
            logger.info("Bot started in normal mode")
            print("Bot running...")
            # Register all command handlers
            bot_command_handlers()
            bot.infinity_polling()
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"System error: {str(e)}")
        print(f"Lỗi hệ thống: {e}")


if __name__ == "__main__":
    initialize_logger()
    os.makedirs("logs", exist_ok=True)
    main()
