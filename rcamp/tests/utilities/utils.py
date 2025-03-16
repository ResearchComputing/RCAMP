import os
import unittest
import importlib
import datetime
import pytz
import logging

from django.test import TestCase
from django.conf import settings

from accounts.models import (
    RcLdapUser,
    RcLdapGroup
)
from accounts.models import User


def assert_test_env():
    """Helper method to verify that tests are not being executed in a production environment."""
    # We can reasonably assume that no production resource will satisfy this criteria, so
    # this is one of several safeguards against running the functional tests against prod.
    assert os.environ.get('RCAMP_DEBUG') == 'True'
    assert settings.DATABASES['rcldap']['PASSWORD'] == 'admin'
    # In an abundance of caution, also make sure that the LDAP and MySQL connections are configured
    # to use the test services.
    assert 'rcamp' in settings.DATABASES['rcldap']['NAME']
    assert 'database' in settings.DATABASES['default']['HOST']
    # Probably not running against prod backends.
    return True

def _assert_test_env_or_false():
    """
    This method returns False if an AssertionError is thrown in assert_test_env. It exists only for
    the unittest.skipUnless decorator, which requires a Boolean value and will not catch exceptions.
    """
    is_test_env = True
    try:
        assert_test_env()
    except AssertionError:
        is_test_env = False
    return is_test_env

def _purge_ldap_objects():
    """Helper method for purging LDAP objects between tests."""
    assert_test_env()
    ldap_users = RcLdapUser.objects.all()
    for user in ldap_users:
        user.delete()
    ldap_groups = RcLdapGroup.objects.all()
    for group in ldap_groups:
        group.delete()

def get_auth_user_defaults():
    """Return a dictionary of reasonable defaults for auth users."""
    auth_user_defaults = dict(
        username = 'testuser',
        password = 'password',
        first_name = 'Test',
        last_name = 'User',
        email = 'testuser@colorado.edu'
    )
    return auth_user_defaults

def localize_timezone(year, month, day, zone):
    """Returns a timezone aware date object"""
    date = datetime.datetime(year, month, day)
    date_tz_aware = pytz.timezone(zone).localize(date)
    return date_tz_aware

@unittest.skipUnless(_assert_test_env_or_false(),"Tests are not being run against a safe test environment!")
class SafeTestCase(TestCase):
    """
    Subclass of the Django framework TestCase that verifies that current host environment does not
    look like a production environment. If the test environment checks fail, then the test case is
    skipped. Class and instance setUp and tearDown methods contain the same checks, as the database
    connection settings can be changed within the context of of individual test cases.

    IMPORTANT: Every unit or integration test should inherit from this class. For functional tests
    user tests.utilities.functional.SafeStaticLiveServerTestCase instead.
    """

    logging.disable(logging.CRITICAL)

    databases = frozenset({'default', 'culdap', 'csuldap', 'rcldap'})

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

class SessionEnabledTestMixin:
    """
    Mixin for Django test cases that use the TestClient that streamlines the process of setting and
    modifying session variables. The get session method expects the TestClient as its only
    argument. Usage:
    >>> session = self.get_session(self.client)
    >>> session['key'] = 'value'
    >>> session.save()
    """
    def _configure_session(self, client):
        engine = importlib.import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self._store = store
        client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def get_session(self, client):
        if not hasattr(self,'_store'):
            self._configure_session(client)
        return self._store
