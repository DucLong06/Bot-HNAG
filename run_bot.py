# run_bot.py
import sys
import time
import subprocess
import argparse
from datetime import datetime
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    "bot_runner.log",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)
logger.add(sys.stderr, level="INFO")  # Also log to console


def run_bot():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true', help='Run the bot continuously')
    args = parser.parse_args()

    if not args.run:
        logger.info("Please use --run flag to start the bot")
        return

    while True:
        try:
            logger.info("Starting bot...")

            # Run the main.py script
            process = subprocess.Popen(
                [sys.executable, 'main.py', '--run'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor the process output
            while True:
                output = process.stdout.readline()
                if output:
                    logger.info(output.strip())

                error = process.stderr.readline()
                if error:
                    logger.error(error.strip())

                # Check if process has ended
                if process.poll() is not None:
                    break

            # If we get here, the process has ended
            return_code = process.poll()

            if return_code != 0:
                logger.error(f"Bot crashed with return code {return_code}")
                remaining_error = process.stderr.read()
                if remaining_error:
                    logger.error(f"Error details: {remaining_error}")
            else:
                logger.warning("Bot process ended normally")

            # Wait before restarting
            logger.info("Waiting 5 seconds before restarting...")
            time.sleep(5)

        except Exception as e:
            logger.error(f"Runner error: {str(e)}")
            logger.info("Waiting 5 seconds before restarting...")
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
