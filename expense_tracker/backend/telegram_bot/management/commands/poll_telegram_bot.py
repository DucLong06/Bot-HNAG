from django.core.management.base import BaseCommand
from django.db import transaction
from telegram_bot.services import TelegramService
from telegram_bot.callback_handlers import PaymentCallbackHandler
from telegram_bot.models import TelegramUpdateOffset
import logging
import fcntl
import os

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Poll Telegram Bot API for updates and process callback queries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Long polling timeout in seconds (default: 30)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

    def handle(self, *args, **options):
        lock_file = '/tmp/telegram_bot_poll.lock'

        try:
            # Acquire lock (non-blocking)
            lock = open(lock_file, 'w')
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Run polling
            timeout = options['timeout']
            verbose = options['verbose']

            if verbose:
                logging.basicConfig(level=logging.DEBUG)

            self.stdout.write(f"[{self._get_timestamp()}] Starting Telegram bot polling...")

            try:
                self._poll_and_process(timeout, verbose)
                self.stdout.write(self.style.SUCCESS(
                    f"[{self._get_timestamp()}] Polling completed successfully"
                ))
            except Exception as e:
                logger.exception("Fatal error in polling command")
                self.stdout.write(self.style.ERROR(
                    f"[{self._get_timestamp()}] Polling failed: {e}"
                ))
                # Don't raise - allow cron to retry next run

        except IOError:
            # Lock already held - another instance running
            self.stdout.write(self.style.WARNING(
                f"[{self._get_timestamp()}] Another instance already running. Skipping."
            ))

        finally:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                lock.close()
            except:
                pass

    def _poll_and_process(self, timeout, verbose):
        """
        Main polling logic.
        Gets updates from Telegram and processes callback queries.
        """
        telegram_service = TelegramService()
        callback_handler = PaymentCallbackHandler()

        # Get updates
        updates = telegram_service.get_telegram_updates(timeout=timeout)

        if not updates:
            if verbose:
                self.stdout.write("No new updates")
            return

        self.stdout.write(f"Processing {len(updates)} update(s)...")

        # Process each update
        processed_count = 0
        error_count = 0

        for update in updates:
            update_id = update.get('update_id')

            try:
                # Only process callback queries (ignore regular messages)
                if 'callback_query' in update:
                    callback_query = update['callback_query']

                    if verbose:
                        self.stdout.write(
                            f"  Processing callback: {callback_query.get('data', 'N/A')}"
                        )

                    # Process callback with handler
                    success = callback_handler.handle_callback_query(callback_query)

                    if success:
                        processed_count += 1
                    else:
                        error_count += 1
                        logger.warning(f"Callback handler returned False for update {update_id}")

                # Update offset after processing (even if not callback_query)
                # This prevents re-processing the same update
                TelegramUpdateOffset.set_offset(update_id)

                if verbose:
                    self.stdout.write(f"  Offset updated to {update_id}")

            except Exception as e:
                error_count += 1
                logger.exception(f"Error processing update {update_id}")
                self.stdout.write(self.style.WARNING(
                    f"  Error in update {update_id}: {e}"
                ))

                # Continue processing other updates (don't break loop)
                # Still update offset to avoid reprocessing failed update
                try:
                    TelegramUpdateOffset.set_offset(update_id)
                except Exception as offset_error:
                    logger.error(f"Failed to update offset: {offset_error}")
                    # This is critical - if offset not updated, will loop forever
                    raise

        # Summary
        self.stdout.write(
            f"Processed: {processed_count}, Errors: {error_count}, Total: {len(updates)}"
        )

    def _get_timestamp(self):
        """Get current timestamp for logging"""
        from django.utils import timezone
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')
