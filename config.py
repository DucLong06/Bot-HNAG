# config.py
import os
from dotenv import load_dotenv
from loguru import logger
import telebot

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# File paths
FOOD_FILE = 'data/food_list.json'
ACTIVE_VOTE_FILE = 'data/active_votes.json'
COMPLETED_VOTE_FILE = 'data/completed_votes.json'

# Initialize bot
if not BOT_TOKEN or not CHAT_ID:
    logger.error("error .env")
    raise ValueError("error .env")

bot = telebot.TeleBot(BOT_TOKEN)


def initialize_logger():
    """Initialize logger configuration"""
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        "logs/active_votes.log",
        rotation="100 MB",
        retention="30 days",
        level="INFO",
        filter=lambda record: "active_vote" in record["extra"],
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        "logs/completed_votes.log",
        rotation="100 MB",
        retention="30 days",
        level="INFO",
        filter=lambda record: "completed_vote" in record["extra"],
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )


# Default data structures
DEFAULT_FOOD_LIST = {
    "foods": [
    ]
}

DEFAULT_VOTE = {
    "active": False,
    "total_amount": 0,
    "payers": [],
    "debtors": [],
    "votes": {}
}
