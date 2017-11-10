from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from selenium import webdriver
from django.contrib.auth.models import User
import datetime
import unittest
import copy

from lib.test.utils import (
    _assert_test_env_or_false,
    assert_test_env,
    _purge_ldap_objects
)

from accounts.models import (
    RcLdapUser,
    RcLdapGroup
)


@unittest.skipUnless(_assert_test_env_or_false(),"Tests are not being run against a safe test environment!")
class SafeStaticLiveServerTestCase(StaticLiveServerTestCase):
    """
    Subclass of the StaticLiveServerTestCase that ensures functional tests are being run against
    the researchcomputing/rc-test-ldap Docker container, and not a prod LDAP server. If the test
    environment checks fail, then the test case is skipped. Class and instance setUp and tearDown
    methods contain the same checks, as the database connection settings can be changed within the
    context of of individual test cases.

    CAUTION: During test set up and tear down, all LDAP users and groups will be purged from
    the configured LDAP backend. For this reason assertions are made to verify the only the
    researchcomputing/rc-test-ldap Docker image is configured. It is imperative that these assumptions not be changed.

    This class depends upon the rc-test-ldap container (https://hub.docker.com/r/researchcomputing/rc-test-ldap/)
    Selenium, and a PhantomJS driver.

    All RCAMP functional tests should inherit from this class.
    """
    @classmethod
    def setUpClass(cls):
        assert_test_env()
        # Start the web driver
        cls.browser = webdriver.PhantomJS()
        cls.browser.set_window_size(1366, 768)
        super(SafeStaticLiveServerTestCase,cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        assert_test_env()
        super(SafeStaticLiveServerTestCase,cls).tearDownClass()

    def setUp(self):
        assert_test_env()
        _purge_ldap_objects()
        super(SafeStaticLiveServerTestCase,self).setUp()

    def tearDown(self):
        assert_test_env()
        _purge_ldap_objects()
        super(SafeStaticLiveServerTestCase,self).tearDown()

class UserAuthenticatedLiveServerTestCase(SafeStaticLiveServerTestCase):
    """
    This subclass of the SafeStaticLiveServerTestCase provides methods for logging a user in and out
    using the selenium webdriver, the currently configured auth backends, and the user (not admin)
    login form. Two pairs of auth/ldap users are created during class set up:
    * un: testuser (UCB) pwd: password
    * un: testuser@colostate.edu (CSU)  pwd: password

    CAUTION: During test set up and tear down, all LDAP users and groups will be purged from
    the configured LDAP backend. For this reason assertions are made to verify the only the
    researchcomputing/rc-test-ldap Docker image is configured. It is imperative that these assumptions not be changed.
    """

    def __init__(self,*args,**kwargs):
        super(UserAuthenticatedLiveServerTestCase,self).__init__(*args,**kwargs)

        self.ucb_user_dn = 'uid=testuser,ou=UCB,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'
        self.csu_user_dn = 'uid=testuser,ou=CSU,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'

        self.ucb_ldap_user_dict = dict(
            username = 'testuser',
            first_name = 'Test',
            last_name = 'User',
            full_name = 'User, Test',
            email = 'testuser@colorado.edu',
            modified_date=datetime.datetime(2015,11,06,03,43,24),
            uid=1010,
            gid=1010,
            gecos='Test User,,,',
            home_directory='/home/testuser'
        )
        self.csu_ldap_user_dict = dict(
            username = 'testuser',
            first_name = 'Test',
            last_name = 'User',
            full_name = 'User, Test',
            email = 'testuser@colostate.edu',
            modified_date=datetime.datetime(2015,11,06,03,43,24),
            uid=1011,
            gid=1011,
            gecos='Test User,,,',
            home_directory='/home/testuser@colostate.edu'
        )
        self.ucb_auth_user_dict = dict(
            username = 'testuser',
            email = 'testuser@colorado.edu',
            password = 'password'
        )
        self.csu_auth_user_dict = dict(
            username = 'testuser@colostate.edu',
            email = 'testuser@colostate.edu',
            password = 'password'
        )

    def _create_user_pairs(self):
        # Create LDAP users to back auth users
        self.ucb_ldap_user = RcLdapUser.objects.create(organization='ucb',**self.ucb_ldap_user_dict)
        self.csu_ldap_user = RcLdapUser.objects.create(organization='csu',**self.csu_ldap_user_dict)
        # Create auth users
        self.ucb_auth_user = User.objects.create_user(
            self.ucb_auth_user_dict['username'],
            self.ucb_auth_user_dict['email'],
            self.ucb_auth_user_dict['password']
        )
        self.csu_auth_user = User.objects.create_user(
            self.csu_auth_user_dict['username'],
            self.csu_auth_user_dict['email'],
            self.csu_auth_user_dict['password']
        )

    def login(self,username='testuser',password='password'):
        """Attempts to log a user in using the RCAMP login form, and the un/pw pair given."""
        # Log into RCAMP
        self.browser.get(self.live_server_url + '/login')
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys(username)
        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys(password)
        self.browser.find_element_by_css_selector('#login-form button').click()

    def logout(self):
        self.browser.get(self.live_server_url + '/logout')

    def setUp(self):
        super(UserAuthenticatedLiveServerTestCase,self).setUp()
        # Create user pairs
        self._create_user_pairs()
