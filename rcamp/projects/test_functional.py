from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.contrib.auth.models import User
import datetime
import mock

from accounts.models import RcLdapUser
from projects.models import Project


project_dict = dict(
    pi_emails = ['testpi@test.org'],
    managers = ['uid=testuser,ou=UCB,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'],
    collaborators = ['uid=testuser,ou=UCB,ou=People,dc=rc,dc=int,dc=colorado,dc=edu'],
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

class ProjectListTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(ProjectListTestCase,cls).setUpClass()
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
        super(ProjectListTestCase,cls).tearDownClass()

    def setUp(self):
        super(ProjectListTestCase,self).setUp()
        # Create test auth user
        username = 'testuser'
        password = 'password'
        self.user = User.objects.create_user(username, 'testuser@test.org', password)
        # Log into RCAMP
        self.browser.get(self.live_server_url + '/login')
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys(username)
        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys(password)
        self.browser.find_element_by_css_selector('#login-form button').click()

    def test_project_list_as_manager(self):
        project = Project.objects.create(**project_dict)
        self.browser.get(self.live_server_url + '/projects/list')
        list_items = self.browser.find_elements_by_css_selector('.list-group > a')
        self.assertIn('/projects/list/{}/'.format(project.pk),list_items[0].get_attribute('href'))
        self.assertIn('/projects/create',list_items[1].get_attribute('href'))

    def test_project_details_as_manager(self):
        project = Project.objects.create(**project_dict)
        self.browser.get(self.live_server_url + '/projects/list/{}/'.format(project.pk))
        # Manager features displayed and active?
        edit_link = self.browser.find_element_by_css_selector('a.project-edit-link')
        reference_create_link = self.browser.find_element_by_css_selector('#reference-add-link')
        request_create_link = self.browser.find_element_by_css_selector('#allocation-request-link')
