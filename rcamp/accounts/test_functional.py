import mock
from unittest import skip
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

@skip("TODO: Update prior to release.")
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
        self.browser.get(self.live_server_url+'/admin/accounts/rcldapgroup/add/')

        organization_option_ucb = self.browser.find_element_by_css_selector('#id_organization > option[value="ucb"]')
        name_input = self.browser.find_element_by_css_selector('#id_name')
        member_option_testuser1_ucb = self.browser.find_element_by_css_selector('#id_members_from > option[value="testuser1"]')
        member_option_testuser2_ucb = self.browser.find_element_by_css_selector('#id_members_from > option[value="testuser2"]')
        members_add_link = self.browser.find_element_by_css_selector('#id_members_add_link')
        save_button = self.browser.find_element_by_css_selector('input[value="Save"]')

        organization_option_ucb.click()
        name_input.send_keys('testgrp')
        member_option_testuser1_ucb.click()
        member_option_testuser2_ucb.click()
        members_add_link.click()
        save_button.click()

        ldap_group = RcLdapGroup.objects.get(name='testgrp')
        group_list_url = '/admin/accounts/rcldapgroup/'
        self.assertIn(group_list_url,self.browser.current_url)

        self.assertEquals(ldap_group.dn.lower(),'cn=testgrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(ldap_group.name,'testgrp')
        self.assertEquals(ldap_group.organization,'ucb')
        self.assertEquals(ldap_group.gid,1003)
        self.assertEquals(set(ldap_group.members),set(['testuser1','testuser2']))

    def test_edit_ldap_group(self):
        ldap_group_defaults = dict(
            name='testcsugrp',
            organization='csu',
            gid=1010,
            members=[]
        )
        ldap_group = RcLdapGroup.objects.create(**ldap_group_defaults)

        edit_url = '/admin/accounts/rcldapgroup/cn_3D{group_name}_2Cou_3Dcsu_2Cou_3Dgroups_2Cdc_3Drc_2Cdc_3Dint_2Cdc_3Dcolorado_2Cdc_3Dedu/'.format(group_name=ldap_group.name)
        self.browser.get(self.live_server_url + edit_url)

        # Verify that dn and organization are readonly or disabled
        dn_input = self.browser.find_element_by_css_selector('#id_dn')
        org_select = self.browser.find_element_by_css_selector('#id_organization')
        org_select_option_csu = self.browser.find_element_by_css_selector('#id_organization > option[value="csu"]')

        self.assertEquals(dn_input.get_attribute('readonly'),'true')
        self.assertEquals(dn_input.get_attribute('value').lower(),ldap_group.dn.lower())
        self.assertEquals(org_select.get_attribute('disabled'),'true')
        self.assertEquals(org_select_option_csu.get_attribute('selected'),'true')

        # Verify member select org filter works
        available_members = self.browser.find_elements_by_css_selector('#id_members_from > option')
        for member in available_members:
            self.assertIn('@colostate.edu',member.get_attribute('title'))

        # Add member and save
        member_option_testuser1 = self.browser.find_element_by_css_selector('#id_members_from > option[value="testuser1"]')
        member_add_link = self.browser.find_element_by_css_selector('#id_members_add_link')
        save_button = self.browser.find_element_by_css_selector('input[value="Save"]')
        member_option_testuser1.click()
        member_add_link.click()
        save_button.click()

        ldap_group = RcLdapGroup.objects.get(name='testcsugrp')
        group_list_url = '/admin/accounts/rcldapgroup/'
        self.assertIn(group_list_url,self.browser.current_url)

        self.assertEquals(ldap_group.org,'csu')
        self.assertEquals(ldap_group.members,['testuser1'])

class LdapUserAdminTestCase(UserAuthenticatedLiveServerTestCase):
    def setUp(self):
        super(LdapUserAdminTestCase,self).setUp()
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

    def test_create_ldap_user(self):
        self.browser.get(self.live_server_url+'/admin/accounts/rcldapuser/add/')

        organization_option_ucb = self.browser.find_element_by_css_selector('#id_organization > option[value="ucb"]')
        username_input = self.browser.find_element_by_css_selector('#id_username')
        full_name_input = self.browser.find_element_by_css_selector('#id_full_name')
        first_name_input = self.browser.find_element_by_css_selector('#id_first_name')
        last_name_input = self.browser.find_element_by_css_selector('#id_last_name')
        email_input = self.browser.find_element_by_css_selector('#id_email')
        home_directory_input = self.browser.find_element_by_css_selector('#id_home_directory')
        save_button = self.browser.find_element_by_css_selector('input[value="Save"]')

        organization_option_ucb.click()
        username_input.send_keys('testuser1')
        full_name_input.send_keys('User, Test')
        first_name_input.send_keys('Test')
        last_name_input.send_keys('User')
        email_input.send_keys('testuser@colorado.edu')
        home_directory_input.send_keys('/home/testuser1/')
        save_button.click()

        ldap_user = RcLdapUser.objects.get(username='testuser1')
        user_list_url = '/admin/accounts/rcldapuser/'
        self.assertIn(user_list_url,self.browser.current_url)

        self.assertEquals(ldap_user.organization,'ucb')
        self.assertEquals(ldap_user.username,'testuser1')
        self.assertEquals(ldap_user.gid,1001)
