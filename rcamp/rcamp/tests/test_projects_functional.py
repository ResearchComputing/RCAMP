from selenium.common.exceptions import NoSuchElementException
from accounts.models import User
import copy

from tests.utilities.utils import get_auth_user_defaults
from tests.utilities.functional import UserAuthenticatedLiveServerTestCase
from projects.models import Project


def get_project_defaults():
    """Return reasonable defaults for non-m2m project fields."""
    project_defaults = dict(
        pi_emails = ['testpi@test.org'],
        organization = 'ucb',
        project_id = 'ucb1',
        title = 'Test project',
        description = 'Test project.'
    )
    return project_defaults

class ProjectDetailsTestCase(UserAuthenticatedLiveServerTestCase):
    def setUp(self):
        super(ProjectDetailsTestCase,self).setUp()
        # Log in as UCB user
        username = self.ucb_auth_user.username
        password = self.ucb_auth_user_dict['password']
        self.login(username,password)

    def test_project_list_as_manager(self):
        project_dict = get_project_defaults()
        project = Project.objects.create(**project_dict)
        project.managers.add(self.ucb_auth_user)
        project.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        self.browser.get(self.live_server_url + '/projects/list')
        list_items = self.browser.find_elements_by_css_selector('.list-group > a')
        self.assertIn('/projects/list/{}/'.format(project.pk),list_items[0].get_attribute('href'))
        self.assertIn('/projects/create',list_items[1].get_attribute('href'))

    def test_project_list_as_suffixed_user(self):
        project_dict = get_project_defaults()
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
        project_dict = get_project_defaults()
        project = Project.objects.create(**project_dict)
        project.managers.add(self.ucb_auth_user)
        project.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        self.browser.get(self.live_server_url + '/projects/list/{}/'.format(project.pk))
        # Manager features displayed and active?
        edit_link = self.browser.find_element_by_css_selector('a.project-edit-link')
        reference_create_link = self.browser.find_element_by_css_selector('#reference-add-link')
        request_create_link = self.browser.find_element_by_css_selector('#allocation-request-link')

    def test_project_details_as_collaborator(self):
        project_dict = get_project_defaults()
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


class ProjectCreateTestCase(UserAuthenticatedLiveServerTestCase):
    def setUp(self):
        super(ProjectCreateTestCase,self).setUp()
        # Log in as UCB user
        username = self.ucb_auth_user.username
        password = self.ucb_auth_user_dict['password']
        self.login(username,password)

    def test_create_project(self):
        project_dict = get_project_defaults()
        project_dict['pi_emails'].append(self.ucb_auth_user.email)

        self.browser.get(self.live_server_url + '/projects/create')

        # Fill out form
        organization_option_ucb = self.browser.find_element_by_css_selector('#id_organization > option[value="ucb"]')
        title_input = self.browser.find_element_by_css_selector('#id_title')
        description_input = self.browser.find_element_by_css_selector('#id_description')
        pi_emails_input = self.browser.find_element_by_css_selector('#id_pi_emails')
        submit_button = self.browser.find_element_by_css_selector('button[type="submit"]')
        # Manager filter select elements
        managers_add_link = self.browser.find_element_by_css_selector('#id_managers_add_link')
        manager_option_ucb_user = self.browser.find_element_by_css_selector('#id_managers_from > option[title="testuser (Test User)"]')
        # Collaborators filter select elements
        collaborators_add_link = self.browser.find_element_by_css_selector('#id_collaborators_add_link')
        collaborator_option_csu_user = self.browser.find_element_by_css_selector('#id_collaborators_from > option[title="testuser@colostate.edu (Test User)"]')

        organization_option_ucb.click()
        title_input.send_keys(project_dict['title'])
        description_input.send_keys(project_dict['description'])
        pi_emails_value = ', '.join(project_dict['pi_emails'])
        pi_emails_input.send_keys(pi_emails_value)
        manager_option_ucb_user.click()
        managers_add_link.click()
        collaborator_option_csu_user.click()
        collaborators_add_link.click()

        submit_button.click()
        project = Project.objects.get(title=project_dict['title'])

        # Redirected to project details view?
        self.assertIn('/projects/list/{}/'.format(project.pk),self.browser.current_url)
        # Verify project attributes
        self.assertEquals(project.organization,project_dict['organization'])
        self.assertEquals(project.title,project_dict['title'])
        self.assertEquals(project.description,project_dict['description'])
        self.assertEquals(project.pi_emails,project_dict['pi_emails'])
        self.assertIn(self.ucb_auth_user,project.managers.all())
        self.assertIn(self.csu_auth_user,project.collaborators.all())


class ProjectEditTestCase(UserAuthenticatedLiveServerTestCase):
    def setUp(self):
        super(ProjectEditTestCase,self).setUp()
        # Log in as UCB user
        username = self.ucb_auth_user.username
        password = self.ucb_auth_user_dict['password']
        self.login(username,password)

    def test_edit_project(self):
        project_dict = get_project_defaults()
        project_dict['pi_emails'].append(self.ucb_auth_user.email)
        project = Project.objects.create(**project_dict)
        project.managers.add(self.ucb_auth_user)
        project.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        self.browser.get(self.live_server_url + '/projects/list/{}/edit'.format(project.pk))

        # Get form fields
        title_input = self.browser.find_element_by_css_selector('#id_title')
        description_input = self.browser.find_element_by_css_selector('#id_description')
        pi_emails_input = self.browser.find_element_by_css_selector('#id_pi_emails')
        submit_button = self.browser.find_element_by_css_selector('button[type="submit"]')
        # Manager filter select elements
        managers_remove_link = self.browser.find_element_by_css_selector('#id_managers_remove_link')
        manager_option_ucb_user = self.browser.find_element_by_css_selector('#id_managers_to > option[title="testuser (Test User)"]')
        # Collaborators filter select elements
        collaborators_remove_link = self.browser.find_element_by_css_selector('#id_collaborators_remove_link')
        collaborator_option_ucb_user = self.browser.find_element_by_css_selector('#id_collaborators_to > option[title="testuser (Test User)"]')
        collaborator_option_csu_user = self.browser.find_element_by_css_selector('#id_collaborators_to > option[title="testuser@colostate.edu (Test User)"]')

        # Verify form data
        form_title_value = title_input.get_attribute('value')
        self.assertEquals(project.title,form_title_value)
        form_description_value = description_input.get_attribute('value')
        self.assertEquals(project.description,form_description_value)
        form_pi_emails_value = pi_emails_input.get_attribute('value')
        pi_emails_rendered = ','.join(project.pi_emails)
        self.assertEquals(pi_emails_rendered,form_pi_emails_value)

        # Modify project fields
        new_pi_emails_value, _ = form_pi_emails_value.split(',')
        pi_emails_input.clear()
        pi_emails_input.send_keys(new_pi_emails_value)

        # Erroneously remove yourself as owner. You should be added back in this case.
        manager_option_ucb_user.click()
        managers_remove_link.click()

        # Remove a collaborator
        collaborator_option_csu_user.click()
        collaborators_remove_link.click()

        submit_button.click()
        # Redirected to project details view?
        self.assertIn('/projects/list/{}/'.format(project.pk),self.browser.current_url)
        project = Project.objects.get(title=project_dict['title'])
        # Verify project attributes
        self.assertEquals(project.organization,project_dict['organization'])
        self.assertEquals(project.title,project_dict['title'])
        self.assertEquals(project.description,project_dict['description'])
        self.assertEquals(project.pi_emails,[new_pi_emails_value])
        self.assertIn(self.ucb_auth_user,project.managers.all())
        self.assertIn(self.ucb_auth_user,project.collaborators.all())
        self.assertNotIn(self.csu_auth_user,project.collaborators.all())
