import time

from django.core.management.base import BaseCommand
from django.db import OperationalError


class Command(BaseCommand):
    help = 'Wait for database until it is ready to accept connections'

    def add_arguments(self, parser):
        # Named (optional) argument
        parser.add_argument(
            '--wait-interval',
            action='store',
            default=1,
            type=float,
            required=False,
            help='If DB is not ready for connections, wait for this number of seconds before next try.',
        )

    def handle(self, *args, **options):
        wait_interval = options['wait_interval']
        db_up = False
        self.stdout.write(f'Waiting for database to be ready for connections, wait interval = {wait_interval}s')

        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except OperationalError:
                self.stdout.write(f'Database unavailable for connections, waiting for {wait_interval}s')
                time.sleep(wait_interval)

        self.stdout.write(self.style.SUCCESS('Database available!'))
