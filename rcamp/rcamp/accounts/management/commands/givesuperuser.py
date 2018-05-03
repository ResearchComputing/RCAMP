from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import datetime
import sys

from lib.test.ldap import get_ldap_user_defaults
from lib.ldap_utils import get_ldap_username_and_org
from accounts.models import (
    User,
    RcLdapUser
)


class Command(BaseCommand):
    help = 'Gives superuser status to the specified user.'

    def add_arguments(self, parser):
        parser.add_argument('--create-user-pair',
            action='store_const',
            const=True,
            help="DEV ONLY. Create a pair of auth and LDAP users."
        )
        parser.add_argument('--alternative-credentials',
            type=str,
            help="DEV ONLY. Set an alternative password for this account."
        )
        parser.add_argument('effective_uid',
            type=str,
            help="Effective UID of user to promote."
        )

    def _create_user_pair(self, effective_uid):
        ldap_user = RcLdapUser.objects.get_user_from_suffixed_username(effective_uid)
        if not ldap_user:
            username, org = get_ldap_username_and_org(effective_uid)
            ldap_user_defaults = get_ldap_user_defaults()
            ldap_user_defaults['username'] = username
            ldap_user_defaults['organization'] = org
            del ldap_user_defaults['uid']
            del ldap_user_defaults['gid']
            ldap_user = RcLdapUser.objects.create(**ldap_user_defaults)

        auth_user_defaults = dict(
            first_name=ldap_user.first_name,
            last_name=ldap_user.last_name,
            email=ldap_user.email
        )
        auth_user, created = User.objects.update_or_create(
            username=effective_uid,
            defaults=auth_user_defaults
        )

        return ldap_user, auth_user

    def handle(self, *args, **options):
        create_user_pair = options.get('create_user_pair',False)
        effective_uid = options.get('effective_uid')
        alternative_credentials = options.get('alternative_credentials',None)

        if create_user_pair:
            ldap_user, auth_user = self._create_user_pair(effective_uid)
        else:
            try:
                auth_user = User.objects.get(username=effective_uid)
            except User.DoesNotExist:
                self.stdout.write('User not found: {username}'.format(username=effective_uid))
                sys.exit(1)

        auth_user.is_staff = True
        auth_user.is_superuser = True
        if alternative_credentials:
            auth_user.set_password(alternative_credentials)
        auth_user.save()
