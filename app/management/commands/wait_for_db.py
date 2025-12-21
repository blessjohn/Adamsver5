# wait_for_db.py
import os
import time
import psycopg2
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        max_retries = 30  # Increased from 5 to allow more time for DB to start
        retry_count = 0
        while retry_count < max_retries:
            try:
                conn = psycopg2.connect(
                    dbname=os.environ.get('DB_NAME'),
                    user=os.environ.get('DB_USER'),
                    password=os.environ.get('DB_PASSWORD'),
                    host=os.environ.get('DB_HOST'),
                    port=os.environ.get('DB_PORT')
                )
                conn.close()
                self.stdout.write(self.style.SUCCESS('Database is ready!'))
                return
            except (psycopg2.OperationalError, psycopg2.Error) as e:
                retry_count += 1
                if retry_count < max_retries:
                    self.stdout.write(f'Database not ready (attempt {retry_count}/{max_retries}), waiting 2 seconds...')
                    time.sleep(2)
                else:
                    self.stdout.write(self.style.ERROR(f'Could not connect to database after {max_retries} retries: {str(e)}'))
                    exit(1)