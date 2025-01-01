# run_bot.py
import sys
import time
import subprocess
import argparse
from datetime import datetime
from loguru import logger
import os
import signal
import psutil

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    "bot_runner.log",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)
logger.add(sys.stderr, level="INFO")


def run_bot():
    parser = argparse.ArgumentParser(description='Bot runner')
    parser.add_argument('--run', action='store_true', help='run bot')
    parser.add_argument('--stop', action='store_true', help='stop bot')
    args = parser.parse_args()

    while True:
        try:
            logger.info("bot...")
            process = subprocess.Popen(
                [sys.executable, 'main.py', '--run'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                if output:
                    logger.info(output.strip())

                error = process.stderr.readline()
                if error:
                    logger.error(error.strip())

                if process.poll() is not None:
                    break

            return_code = process.poll()
            if return_code != 0:
                logger.error(f"Bot crash {return_code}")
                remaining_error = process.stderr.read()
                if remaining_error:
                    logger.error(f"error: {remaining_error}")
            else:
                logger.warning("Bot stop")

            logger.info("Wait 5 second...")
            time.sleep(5)

        except Exception as e:
            logger.error(f"Lỗi runner do Nam: {str(e)}")
            logger.info("Wait 5 second...")
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
