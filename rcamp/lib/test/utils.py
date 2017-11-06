from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.contrib.auth.models import User
import datetime
import mock
import copy

from accounts.models import RcLdapUser


class UserAuthenticatedLiveServerTestCase(StaticLiveServerTestCase):
    """
    This subclass of the StaticLiveServerTestCase provides methods for logging a user in and out
    using the selenium webdriver, the currently configured auth backends, and the user (not admin)
    login form. Two pairs of auth/ldap users are created during class set up:
    * un: testuser (UCB) pwd: password
    * un: testuser@colostate.edu (CSU)  pwd: password

    CAUTION: Before instance set up and tear down, all LDAP users and groups will be purged from
    the .

    This class depends upon the rc-test-ldap container (https://hub.docker.com/r/researchcomputing/rc-test-ldap/)
    Selenium, and a PhantomJS driver.
    """

    def __init__(self,*args,**kwargs):
        super(UserAuthenticatedLiveServerTestCase,self).__init__(*args,**kwargs)

        self.ucb_user_dn = 'uid=testuser,ou=UCB,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'
        self.csu_user_dn = 'uid=testuser,ou=CSU,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'

        self.ldap_user_dict = dict(
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

    @classmethod
    def setUpClass(cls):
        super(ProjectDetailsTestCase,cls).setUpClass()
        cls._purge_ldap_objects()
        # Start the web driver
        cls.browser = webdriver.PhantomJS()
        cls.browser.set_window_size(1366, 768)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls._purge_ldap_objects()
        super(ProjectDetailsTestCase,cls).tearDownClass()

    @classmethod
    def _purge_ldap_objects(cls):
        ldap_users = RcLdapUser.objects.all()
        for user in ldap_users:
            user.delete()
        ldap_groups = RcLdapGroup.objects.all()
        for group in ldap_groups:
            group.delete()

    def _create_user_pairs(self):
        # Create LDAP users to back auth users
        ucb_ldap_user = RcLdapUser.objects.create(organization='ucb',**ldap_user_dict)
        csu_ldap_user = RcLdapUser.objects.create(organization='csu',**csu_ldap_user_dict)

    def _login(self,username,password):
        # Log into RCAMP
        self.browser.get(self.live_server_url + '/login')
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys(username)
        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys(password)
        self.browser.find_element_by_css_selector('#login-form button').click()

    def _logout(self):
        self.browser.get(self.live_server_url + '/logout')

    def setUp(self):
        super(ProjectDetailsTestCase,self).setUp()
        # Create test auth user
        username = 'testuser'
        password = 'password'
        self.user = User.objects.create_user(username,'testuser@test.org',password)
        self._login(username,password)
        # Add a suffixed user to LDAP
        csu_ldap_user_dict = copy.deepcopy(ldap_user_dict)
        csu_ldap_user_dict['uid'] = 1011
        csu_ldap_user_dict['gid'] = 1011
        try:
            csu_ldap_user = RcLdapUser.objects.create(organization='csu',**csu_ldap_user_dict)
        except:
            pass
