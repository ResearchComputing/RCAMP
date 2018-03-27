from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import datetime

from lib.ldap_utils import get_ldap_username_and_org
from accounts.models import (
    User,
    RcLdapUser
)


class Command(BaseCommand):
    help = 'Syncs RCAMP auth users with RC LDAP.'

    def add_arguments(self, parser):
        parser.add_argument('--delete',
            action='store_const',
            const=True,
            help="Delete auth users not found in LDAP."
        )
        parser.add_argument('--quiet',
            action='store_const',
            const=True,
            help="Suppress log messages."
        )

    def _log_message(self,message,quiet=False,message_type='stdout'):
        if (not quiet) and (message_type == 'stdout'):
            self.stdout.write(message)
        if message_type == 'stderr':
            self.stderr.write(message)

    def handle(self, *args, **options):
        delete = options.get('delete',False)
        quiet = options.get('quiet',False)
        auth_users_remaining = [user.username for user in User.objects.all()]
        rc_ldap_users = RcLdapUser.objects.all()

        for ldap_user in rc_ldap_users:
            user_defaults = dict(
                email=ldap_user.email,
                first_name=ldap_user.first_name,
                last_name=ldap_user.last_name
            )
            auth_user, created = User.objects.update_or_create(
                username=ldap_user.effective_uid,
                defaults=user_defaults
            )

            if created:
                self._log_message(
                    'Created user {username}'.format(username=auth_user.username),
                    quiet=quiet
                )
            else:
                auth_users_remaining.remove(auth_user.username)

        user_list = '\n'.join(auth_users_remaining)
        if delete:
            User.objects.filter(username__in=auth_users_remaining).delete()
            self._log_message(
                'The following users were deleted:\n{user_list}'.format(user_list=user_list),
                quiet=quiet
            )
        else:
            user_list = '\n'.join(auth_users_remaining)
            self._log_message(
                'The following users were not found in LDAP, but exist in RCAMP:\n{user_list}\nUse the --delete option to remove these users from RCAMP.'.format(user_list=user_list),
                quiet=quiet
            )
