import mock
from lib.test.ldap import (
    get_ldap_user_defaults,
    get_ldap_group_defaults
)
from lib.test.functional import (
    SafeStaticLiveServerTestCase,
    UserAuthenticatedLiveServerTestCase
)

from accounts.models import (
    IdTracker,
    AccountRequest,
    RcLdapUser,
    RcLdapGroup
)


def get_request_form_defaults():
    """Returns a dictionary containing reasonable defaults for account requests forms."""
    request_form_defaults = dict(
        organization = 'ucb',
        username = 'testuser',
        password = 'testpass',
        login_shell = '/bin/bash',
        role = 'faculty',
        summit = True,
        petalibrary_archive = True,
    )
    return request_form_defaults

def get_org_user_defaults():
    """Returns a dictionary of reasonable defaults for users returned from external LDAPs."""
    defaults = dict(
        username = 'testuser',
        first_name = 'Test',
        last_name = 'User',
        email = 'testuser@colorado.edu'
    )
    return defaults

class AccountRequestGeneralTestCase(SafeStaticLiveServerTestCase):
    def setUp(self):
        super(AccountRequestGeneralTestCase,self).setUp()
        self.browser.get(self.live_server_url+'/accounts/account-request/create/general')

    def test_request_create(self):
        request_form_defaults = get_request_form_defaults()
        # Org select field
        org_options = self.browser.find_elements_by_css_selector('#id_organization > option')
        self.assertEquals(len(org_options),2)
        self.assertEquals(org_options[0].get_attribute('value'),'ucb')
        self.assertEquals(org_options[1].get_attribute('value'),'csu')

        # Fill out form
        organization_option_ucb = self.browser.find_element_by_css_selector('#id_organization > option[value="ucb"]')
        username_input = self.browser.find_element_by_css_selector('#id_username')
        password_input = self.browser.find_element_by_css_selector('#id_password')
        role_option_faculty = self.browser.find_element_by_css_selector('#id_role > option[value="faculty"]')
        summit_checkbox = self.browser.find_element_by_css_selector('#id_summit')
        blanca_checkbox = self.browser.find_element_by_css_selector('#id_blanca')
        submit_button = self.browser.find_element_by_css_selector('button[type="submit"]')

        organization_option_ucb.click()
        role_option_faculty.click()
        summit_checkbox.click()
        blanca_checkbox.click()
        username_input.send_keys(request_form_defaults['username'])
        password_input.send_keys(request_form_defaults['password'])

        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user_manager_get = mock.MagicMock(return_value=mock_cu_user)
        mock_cu_user_authenticated = mock.MagicMock(return_value=True)
        with mock.patch('accounts.models.CuLdapUser.objects.get',mock_cu_user_manager_get):
            with mock.patch('accounts.models.CuLdapUser.authenticate',mock_cu_user_authenticated):
                submit_button.click()

        # Acknowledge contact info
        # self.browser.implicitly_wait(1)
        # email_ack_checkbox = self.browser.find_element_by_css_selector('#email_ack')
        # submit_ack_button = self.browser.find_element_by_css_selector('#submit_ack')
        # email_ack_checkbox.click()
        # submit_ack_button.click()

        account_request = AccountRequest.objects.get(username='testuser')
        review_url = '/account-request/review/{}'.format(account_request.pk)
        self.assertIn(review_url,self.browser.current_url)
        self.assertIn(mock_cu_user.email,self.browser.page_source)

        self.assertEquals(account_request.first_name,'Test')
        self.assertEquals(account_request.last_name,'User')
        self.assertEquals(account_request.email,'testuser@colorado.edu')
        self.assertEquals(account_request.role, 'faculty')
        self.assertEquals(account_request.login_shell,'/bin/bash')
        self.assertEquals(account_request.resources_requested,'blanca,summit')
        self.assertEquals(account_request.organization,'ucb')

class LdapGroupAdminTestCase(UserAuthenticatedLiveServerTestCase):
    def setUp(self):
        super(LdapGroupAdminTestCase,self).setUp()
        # Log in as UCB user
        username = self.ucb_auth_user.username
        password = self.ucb_auth_user_dict['password']
        self.login(username,password)

        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )

        # Create LDAP users to populate member select
        ldap_user_defaults = get_ldap_user_defaults()
        ldap_user_defaults['username'] = 'testuser1'
        ldap_user_defaults['organization'] = 'ucb'
        ldap_user_defaults['uid'] = 1000
        ldap_user_defaults['gid'] = 1000
        RcLdapUser.objects.create(**ldap_user_defaults)
        ldap_user_defaults['username'] = 'testuser2'
        ldap_user_defaults['organization'] = 'ucb'
        ldap_user_defaults['uid'] = 1002
        ldap_user_defaults['gid'] = 1002
        RcLdapUser.objects.create(**ldap_user_defaults)
        ldap_user_defaults['username'] = 'testuser1'
        ldap_user_defaults['organization'] = 'csu'
        ldap_user_defaults['uid'] = 1001
        ldap_user_defaults['gid'] = 1001
        RcLdapUser.objects.create(**ldap_user_defaults)

    def test_create_ldap_group(self):
        ldap_group_defaults = get_ldap_group_defaults()

        self.browser.get(self.live_server_url+'/admin/accounts/rcldapgroup/add/')

        organization_option_ucb = self.browser.find_element_by_css_selector('#id_organization > option[value="ucb"]')
        name_input = self.browser.find_element_by_css_selector('#id_name')
        member_option_testuser1_ucb = self.browser.find_element_by_css_selector('#id_members_from > option[value="testuser1"]')
        members_add_link = self.browser.find_element_by_css_selector('#id_members_add_link')
        save_button = self.browser.find_element_by_css_selector('input[value="Save"]')

        organization_option_ucb.click()
        name_input.send_keys('testgrp')
        member_option_testuser1_ucb.click()
        members_add_link.click()
        save_button.click()

        ldap_group = RcLdapGroup.objects.get(name='testgrp')
        group_list_url = '/admin/accounts/rcldapgroup/'
        self.assertIn(group_list_url,self.browser.current_url)
