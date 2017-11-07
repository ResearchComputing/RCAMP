from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
import copy

from lib.test.utils import UserAuthenticatedLiveServerTestCase
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

class ProjectDetailsTestCase(UserAuthenticatedLiveServerTestCase):
    def setUp(self):
        super(ProjectDetailsTestCase,self).setUp()
        # Log in as UCB user
        username = self.ucb_auth_user.username
        password = self.ucb_auth_user_dict['password']
        self.login(username,password)

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
        # Log in as CSU user
        username = self.csu_auth_user.username
        password = self.csu_auth_user_dict['password']
        self.logout()
        self.login(username,password)

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
