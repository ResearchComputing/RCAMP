from lib.test.utils import (
    _purge_ldap_objects,
    SafeTestCase
)
import copy
import datetime
import mock


def get_ldap_user_defaults():
    """Return a dictionary of reasonable defaults for creating RcLdapUser objects via the ORM."""
    ldap_user_defaults = dict(
        username = 'testuser',
        first_name = 'Test',
        last_name = 'User',
        full_name = 'User, Test',
        email = 'testuser@colorado.edu',
        modified_date=datetime.datetime(2015,11,06,03,43,24),
        uid = 1010,
        gid = 1010,
        gecos='Test User,,,',
        home_directory='/home/testuser'
    )
    return ldap_user_defaults

def get_ldap_group_defaults():
    """Return a dictionary of reasonable defaults for creating RcLdapGroup objects via the ORM."""
    ldap_group_defaults = dict(
        name = 'testusergrp',
        gid = 1010,
        members = ['testuser']
    )
    return ldap_group_defaults

def build_mock_rcldap_user(**kwargs):
    """
    Constructs a MagicMock object to represent an RcLdapUser. Takes available RcLdapUser attributes
    as optional keyword arguments to replace default values.
    """
    ldap_user_defaults = get_ldap_user_defaults()
    ldap_user_defaults['dn'] = 'uid=testuser,ou=UCB,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'
    ldap_user_defaults.update(kwargs)
    mock_ldap_user = mock.MagicMock(**ldap_user_defaults)
    return mock_ldap_user

def build_mock_rcldap_group(**kwargs):
    """
    Constructs a MagicMock object to represent an RcLdapGroup. Takes available RcLdapGroup
    attributes as optional keyword arguments to replace default values.
    """
    ldap_group_defaults = get_ldap_group_defaults()
    ldap_group_defaults.update(kwargs)
    mock_ldap_group = mock.MagicMock(**ldap_group_defaults)
    return mock_ldap_group

class LdapTestCase(SafeTestCase):
    """
    Subclass of SafeTestCase that add functionality for integration tests dependent upon a live
    LDAP server.

    CAUTION: During test set up and tear down, all LDAP users and groups will be purged from
    the configured LDAP backend. For this reason assertions are made to verify the only the
    researchcomputing/rc-test-ldap Docker image is configured. It is imperative that these assumptions not be changed.
    """
    @classmethod
    def setUpClass(cls):
        super(LdapTestCase,cls).setUpClass()
        _purge_ldap_objects()

    def tearDown(self):
        _purge_ldap_objects()
        super(LdapTestCase,self).setUpClass()
