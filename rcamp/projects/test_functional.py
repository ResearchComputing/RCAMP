from selenium.common.exceptions import NoSuchElementException
from accounts.models import User
import copy

from lib.test.utils import get_auth_user_defaults
from lib.test.functional import UserAuthenticatedLiveServerTestCase
from projects.models import Project


project_dict = dict(
    pi_emails = ['testpi@test.org'],
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
        project.managers.add(self.ucb_auth_user)
        project.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        self.browser.get(self.live_server_url + '/projects/list')
        list_items = self.browser.find_elements_by_css_selector('.list-group > a')
        self.assertIn('/projects/list/{}/'.format(project.pk),list_items[0].get_attribute('href'))
        self.assertIn('/projects/create',list_items[1].get_attribute('href'))

    def test_project_list_as_suffixed_user(self):
        project = Project.objects.create(**project_dict)
        project.managers.add(self.csu_auth_user)
        project.collaborators.add(self.csu_auth_user,self.ucb_auth_user)

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
        project.managers.add(self.ucb_auth_user)
        project.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        self.browser.get(self.live_server_url + '/projects/list/{}/'.format(project.pk))
        # Manager features displayed and active?
        edit_link = self.browser.find_element_by_css_selector('a.project-edit-link')
        reference_create_link = self.browser.find_element_by_css_selector('#reference-add-link')
        request_create_link = self.browser.find_element_by_css_selector('#allocation-request-link')

    def test_project_details_as_collaborator(self):
        project = Project.objects.create(**project_dict)
        project.managers.add(self.csu_auth_user)
        project.collaborators.add(self.csu_auth_user,self.ucb_auth_user)

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
        self.assertIn('testuser@colostate.edu',manager_list_td.text)
        collaborator_list_td = self.browser.find_element_by_css_selector("#table-collaborator_list-row td:nth-child(2)")
        self.assertIn('testuser@colostate.edu',collaborator_list_td.text)
        self.assertIn('testuser',collaborator_list_td.text)
