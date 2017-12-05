from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import datetime
import sys

from accounts.models import (
    User
)


class Command(BaseCommand):
    help = 'Gives superuser status to the specified user.'

    def add_arguments(self, parser):
        parser.add_argument('--alternative-credentials',
            type=str,
            help="DEV ONLY. Set an alternative password for this account."
        )
        parser.add_argument('effective_uid',
            type=str,
            help="Effective UID of user to promote."
        )

    def handle(self, *args, **options):
        effective_uid = options.get('effective_uid')
        alternative_credentials = options.get('alternative_credentials',None)

        try:
            user = User.objects.get(username=effective_uid)
            user.is_staff = True
            user.is_superuser = True
            if alternative_credentials:
                user.set_password(alternative_credentials)
            user.save()
        except User.DoesNotExist:
            self.stdout.write('User not found: {username}'.format(username=effective_uid))
            sys.exit(1)
