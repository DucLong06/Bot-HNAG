import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection, transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Restore data from a JSON file with safety checks'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the backup JSON file')

    def handle(self, *args, **options):
        backup_file = options['backup_file']

        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f'File not found: {backup_file}'))
            return

        self.stdout.write(self.style.WARNING('Starting data restoration...'))

        # 1. Clear existing data (optional but recommended for clean restore)
        # Uncomment the next line if you want to wipe the DB first.
        # Be extremely careful with this in production!
        # call_command('flush', '--no-input')

        # 2. Import data
        try:
            with transaction.atomic():
                # Disable constraint checks (PostgreSQL specific, SQLite handles differently)
                # This is a bit risky but necessary for circular dependencies sometimes
                # However, dumpdata --natural-foreign usually solves this.

                self.stdout.write('Loading data...')
                call_command('loaddata', backup_file)

                self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            return  # Stop if data loading fails

        # 3. Fix sequences (Quan trọng cho Postgres sau khi import ID thủ công)
        # Nếu không làm bước này, khi bạn insert record mới sẽ bị lỗi Duplicate Key
        if connection.vendor == 'postgresql':
            self.stdout.write('Resetting sequences for PostgreSQL...')

            # Cách chuẩn của Django để reset sequence
            from django.apps import apps
            from django.core.management.color import no_style

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), apps.get_models())
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

            self.stdout.write(self.style.SUCCESS('Sequences reset successfully!'))
