from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
import unittest

from accounts.models import (
    RcLdapUser,
    RcLdapGroup
)


def assert_test_env():
    """Helper method to verify that tests are not being executed in a production environment."""
    # We can reasonably assume that no production resource will satisfy this criteria, so
    # this is one of several safeguards against running the functional tests against prod.
    assert settings.DATABASES['rcldap']['PASSWORD'] == 'password'
    # In an abundance of caution, also make sure that the LDAP connection is configured
    # to use localhost.
    assert 'localhost' in settings.DATABASES['rcldap']['NAME']
    # Probably not running against prod LDAP.
    return True

def _purge_ldap_objects():
    """Helper method for purging LDAP objects between tests."""
    assert_test_env()
    ldap_users = RcLdapUser.objects.all()
    for user in ldap_users:
        user.delete()
    ldap_groups = RcLdapGroup.objects.all()
    for group in ldap_groups:
        group.delete()

@unittest.skipUnless(assert_test_env(),"Tests are not being run against a safe test environment!")
class SafeTestCase(TestCase):
    """
    Subclass of the Django framework TestCase that verifies that current host environment does not
    look like a production environment. If the test environment checks fail, then the test case is
    skipped. Class and instance setUp and tearDown methods contain the same checks, as the database
    connection settings can be changed within the context of of individual test cases.

    IMPORTANT: Every unit or integration test should inherit from this class. For functional tests
    user lib.test.functional.SafeStaticLiveServerTestCase instead.
    """
    @classmethod
    def setUpClass(cls):
        assert_test_env()
        super(SafeTestCase,cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        assert_test_env()
        super(SafeTestCase,cls).tearDownClass()

    def setUp(self):
        assert_test_env()
        super(SafeTestCase,self).setUp()

    def tearDown(self):
        assert_test_env()
        super(SafeTestCase,self).tearDown()
