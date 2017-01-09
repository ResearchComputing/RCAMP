from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import pam
import copy

from django.conf import settings

from accounts.forms import AccountRequestForm
from accounts.forms import SponsoredAccountRequestForm
from accounts.forms import ClassAccountRequestForm
from accounts.forms import ProjectAccountRequestForm
from accounts.admin import AccountRequestAdminForm
from accounts.models import CuLdapUser
from accounts.models import CsuLdapUser
from accounts.models import AccountRequest
from accounts.test_models import BaseCase
from projects.models import Project


#Mock CU LDAP
admin = ('cn=admin', {'userPassword': ['test']})
people = ('ou=users,dc=colorado,dc=edu', {
    'objectClass': [], 'ou': ['users']})
test_user = (
    'uid=testuser,ou=users,dc=colorado,dc=edu', {
        'objectClass': [],
        'cn': ['user, test'],
        'givenName': ['test'],
        'sn': ['user'],
        'mail': ['testuser@test.org'],
        'uid': ['testuser'],
        'modifytimestamp': ['20151106034324Z'],
    }
)

# Base class to set up mock LDAP server for the remainder
# of the test cases.
#
# In each test that interacts with the mock LDAP, the
# DATABASE_ROUTERS setting will need to be overridden
# with the LDAP router for test.
class CuBaseCase(BaseCase):
    directory = dict([admin, people, test_user])

    def setUp(self):
        self.mockldap.start()
        self.ldapobj = self.mockldap[settings.DATABASES['culdap_test']['NAME']]

# Cursory test to ensure mock LDAP is properly configured
class MockCuLdapTestCase(CuBaseCase):
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_cuuser_read(self):
        u = CuLdapUser.objects.get(username='testuser')

        self.assertEquals(u.username, 'testuser')
        self.assertEquals(u.modified_date, datetime.datetime(2015,11,06,03,43,24))

        self.assertRaises(CuLdapUser.DoesNotExist, CuLdapUser.objects.get,
                        username='does_not_exist')

# This test case covers the functionality of the general account request form
# delivered to the user during account request. MagicMock is
# used as a stopgap while authentication against CU LDAP
# remains untestable.
class AccountRequestFormTestCase(CuBaseCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid(self):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'login_shell': '/bin/bash',
        }
        form = AccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_bad_user(self):
        form_data = {
            'organization': 'ucb',
            'username': 'wronguser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=False))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_bad_password(self):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    # CSU request tests
    @mock.patch('accounts.models.CsuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def xtest_csu_form_valid(self):
        form_data = {
            'organization': 'csu',
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'login_shell': '/bin/bash',
        }
        form = AccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('accounts.models.CsuLdapUser.authenticate',MagicMock(return_value=False))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_csu_form_invalid_bad_creds(self):
        form_data = {
            'organization': 'csu',
            'username': 'wronguser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_missing_fields(self):
        form_data = {
            'username': 'testuser',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data = {
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

# This test case covers the functionality of the account request form
# provided in the admin interface.
class AccountRequestAdminFormTestCase(BaseCase):
    def setUp(self):
        super(AccountRequestAdminFormTestCase,self).setUp()
        self.ar_dict = {
            'organization': 'ucb',
            'username': 'testuser',
            'first_name': 'test',
            'last_name': 'user',
            'email': 'testuser@test.org',
            'role': 'faculty',
            'login_shell': '/bin/bash',
            'status': 'p'
        }

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid_create_approve_request(self):
        form_data = {
            'organization': 'ucb',
            'username': 'newtestuser',
            'first_name': 'test',
            'last_name': 'user',
            'email': 'newtestuser@test.org',
            'role': 'faculty',
            'login_shell': '/bin/bash',
            'status': 'p'
        }
        form = AccountRequestAdminForm(data=form_data)
        self.assertTrue(form.is_valid())

        ar = AccountRequest.objects.create(**form_data)
        form_data['status'] = 'a'

        form = AccountRequestAdminForm(data=form_data,instance=ar)
        self.assertTrue(form.is_valid())

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid_request_modified(self):
        ar = AccountRequest.objects.create(**self.ar_dict)
        form_data = copy.deepcopy(self.ar_dict)
        form_data['role'] = 'student'

        form = AccountRequestAdminForm(data=form_data,instance=ar)
        self.assertTrue(form.is_valid())

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_approval_account_exists(self):
        ar = AccountRequest.objects.create(**self.ar_dict)
        form_data = copy.deepcopy(self.ar_dict)
        form_data['status'] = 'a'

        form = AccountRequestAdminForm(data=form_data,instance=ar)
        self.assertFalse(form.is_valid())

class AccountRequestFormRcLdapTestCase(BaseCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_user_exists(self):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_accountrequest_exists(self):
        ar_dict = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'tu@tu.org',
            'organization': 'ucb',
            'role': 'faculty',
            'login_shell': '/bin/bash',
        }
        ar = AccountRequest.objects.create(**ar_dict)
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'login_shell': '/bin/bash',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

# This test case covers the functionality of the sponsored account request form
# delivered to the user during account request.
class SponsoredAccountRequestFormTestCase(CuBaseCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'sponsor_email': 'sponsor@colorado.edu',
            'login_shell': '/bin/bash',
        }
        form = SponsoredAccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['role'], 'sponsored')
        self.assertEqual(form.cleaned_data['organization'], 'ucb')

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_missing_fields(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = SponsoredAccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

# This test case covers the functionality of the class account request form
# delivered to the user during account request.
class ClassAccountRequestFormTestCase(CuBaseCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'course_number': 'CSCI4000',
            'login_shell': '/bin/bash',
        }
        form = ClassAccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['role'], 'student')
        self.assertEqual(form.cleaned_data['organization'], 'ucb')

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_invalid_missing_fields(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = ClassAccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

# This test case covers the functionality of the project account request form
# delivered to the user during account request.
class ProjectAccountRequestFormTestCase(CuBaseCase):
    def setUp(self):
        proj_dict = {
            'pi_emails': ['testpiuser@test.org'],
            'managers': ['testpiuser'],
            'collaborators': ['testpiuser'],
            'organization': 'ucb',
            'project_id': 'ucb1',
            'title': 'Test project',
            'description': 'Test project.',
        }
        Project.objects.create(**proj_dict)
        proj_dict.update({
            'project_id': 'ucb2',
            'title': 'Test project 2',
            'description': 'Test project 2.',
        })
        Project.objects.create(**proj_dict)
        super(ProjectAccountRequestFormTestCase,self).setUp()

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid(self):
        form_data = {
            'projects': [proj.pk for proj in Project.objects.all()],
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
            'role': 'student',
            'login_shell': '/bin/bash',
        }
        form = ProjectAccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_form_valid_missing_fields(self):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
            'role': 'student',
            'login_shell': '/bin/bash',
        }
        form = ProjectAccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
