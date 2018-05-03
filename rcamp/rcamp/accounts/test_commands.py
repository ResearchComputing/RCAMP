from django.test import override_settings
import mock
import datetime
import ldap
import copy

from django.conf import settings
from django.core.management import call_command

from lib.test.utils import SafeTestCase
from lib.test.ldap import (
    get_ldap_user_defaults,
    get_ldap_group_defaults,
    build_mock_rcldap_user,
    build_mock_rcldap_group,
    LdapTestCase
)

from accounts.models import (
    IdTracker,
    AccountRequest,
    RcLdapUser,
    RcLdapGroup
)


class SyncLdapUserTestCase(LdapTestCase):
    def test_sync_no_delete(self):
        ldap_user_dict = get_ldap_user_defaults()
