# wait_for_db.py
import os
import time
import psycopg2
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        max_retries = 5
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
            except psycopg2.OperationalError:
                self.stdout.write('Database not ready, waiting 2 seconds...')
                time.sleep(2)
                retry_count += 1
        self.stdout.write(self.style.ERROR('Could not connect to database after retries'))
        exit(1)