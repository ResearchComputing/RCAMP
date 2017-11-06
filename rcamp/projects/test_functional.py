from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
import datetime
import mock
import copy

from accounts.models import RcLdapUser
from projects.models import Project


ucb_user_dn = 'uid=testuser,ou=UCB,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'
csu_user_dn = 'uid=testuser,ou=CSU,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'

project_dict = dict(
    pi_emails = ['testpi@test.org'],
    managers = [ucb_user_dn],
    collaborators = [ucb_user_dn,csu_user_dn],
    organization = 'ucb',
    project_id = 'ucb1',
    title = 'Test project',
    description = 'Test project.'
)

ldap_user_dict = dict(
    username = 'testuser',
    first_name = 'Test',
    last_name = 'User',
    full_name = 'User, Test',
    email = 'testuser@test.org',
    modified_date=datetime.datetime(2015,11,06,03,43,24),
    uid=1010,
    gid=1010,
    gecos='Test User,,,',
    home_directory='/home/testuser'
)

class ProjectDetailsTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(ProjectDetailsTestCase,cls).setUpClass()
        # Start the web driver
        cls.browser = webdriver.PhantomJS()
        cls.browser.set_window_size(1366, 768)
        # Create LDAP user to back auth user
        try:
            ldap_user = RcLdapUser.objects.create(organization='ucb',**ldap_user_dict)
        except:
            pass

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(ProjectDetailsTestCase,cls).tearDownClass()

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

    def test_project_list_as_manager(self):
        project = Project.objects.create(**project_dict)
        self.browser.get(self.live_server_url + '/projects/list')
        list_items = self.browser.find_elements_by_css_selector('.list-group > a')
        self.assertIn('/projects/list/{}/'.format(project.pk),list_items[0].get_attribute('href'))
        self.assertIn('/projects/create',list_items[1].get_attribute('href'))

    def test_project_list_as_suffixed_user(self):
        csu_project_dict = copy.deepcopy(project_dict)
        csu_project_dict['managers'] = [csu_user_dn]
        csu_project_dict['collaborators'] = [csu_user_dn,ucb_user_dn]
        project = Project.objects.create(**csu_project_dict)
        # Create test CSU auth user
        username = 'testuser@colostate.edu'
        password = 'password'
        self.user = User.objects.create_user(username,'testuser@csutest.org',password)
        self._logout()
        self._login(username,password)
        self.browser.get(self.live_server_url + '/projects/list')
        list_items = self.browser.find_elements_by_css_selector('.list-group > a')
        self.assertIn('/projects/list/{}/'.format(project.pk),list_items[0].get_attribute('href'))

    def test_project_details_as_manager(self):
        project = Project.objects.create(**project_dict)
        self.browser.get(self.live_server_url + '/projects/list/{}/'.format(project.pk))
        # Manager features displayed and active?
        edit_link = self.browser.find_element_by_css_selector('a.project-edit-link')
        reference_create_link = self.browser.find_element_by_css_selector('#reference-add-link')
        request_create_link = self.browser.find_element_by_css_selector('#allocation-request-link')

    def test_project_details_as_collaborator(self):
        collab_project_dict = copy.deepcopy(project_dict)
        collab_project_dict['managers'] = [csu_user_dn]
        collab_project_dict['collaborators'] = [csu_user_dn,ucb_user_dn]
        project = Project.objects.create(**collab_project_dict)
        self.browser.get(self.live_server_url + '/projects/list/{}/'.format(project.pk))
        # Manager features disabled?
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('a.project-edit-link')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#reference-add-link')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#allocation-request-link')
        # Member fields render suffixed and unsuffixed names correctly?
        manager_list_td = self.browser.find_element_by_css_selector("#table-manager_list-row td:nth-child(2)")
        self.assertEqual(manager_list_td.text,'testuser@colostate.edu')
        collaborator_list_td = self.browser.find_element_by_css_selector("#table-collaborator_list-row td:nth-child(2)")
        self.assertEqual(collaborator_list_td.text,'testuser@colostate.edu,  testuser')
