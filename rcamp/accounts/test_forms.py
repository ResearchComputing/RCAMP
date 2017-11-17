from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import pam
import copy

from django.conf import settings
from lib.test.ldap import LdapTestCase

from accounts.forms import (
    AccountRequestForm,
    SponsoredAccountRequestForm,
    ClassAccountRequestForm,
    # ProjectAccountRequestForm
)
from accounts.admin import AccountRequestAdminForm
from accounts.models import (
    CuLdapUser,
    CsuLdapUser,
    AccountRequest
)
# from projects.models import Project


mock_cu_user_defaults = dict(
    username = 'testuser',
    first_name = 'Test',
    last_name = 'User',
    email = 'testuser@test.org'
)
mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
mock_csu_user = mock.MagicMock(**mock_cu_user_defaults)

# This test case covers the functionality of the general account request form
# delivered to the user during account request. MagicMock is
# used as a stopgap while authentication against CU LDAP
# remains untestable.
class AccountRequestFormTestCase(LdapTestCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_valid(self,mock_get,mock_auth):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'login_shell': '/bin/bash',
        }
        form = AccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',side_effect=[CuLdapUser.DoesNotExist])
    def test_form_invalid_bad_user(self,mock_get,mock_auth):
        form_data = {
            'organization': 'ucb',
            'username': 'wronguser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=False)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_bad_password(self,mock_get,mock_auth):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    # CSU request tests
    @mock.patch('accounts.models.CsuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user)
    def test_csu_form_valid(self,mock_get,mock_auth):
        form_data = {
            'organization': 'csu',
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'login_shell': '/bin/bash',
        }
        form = AccountRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('accounts.models.CsuLdapUser.authenticate',return_value=False)
    @mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user)
    def test_csu_form_invalid_bad_creds(self,mock_get,mock_auth):
        form_data = {
            'organization': 'csu',
            'username': 'wronguser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_missing_fields(self,mock_get,mock_auth):
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
class AccountRequestAdminFormTestCase(LdapTestCase):
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

    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_valid_create_approve_request(self,mock_get):
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

    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_valid_request_modified(self,mock_get):
        ar = AccountRequest.objects.create(**self.ar_dict)
        form_data = copy.deepcopy(self.ar_dict)
        form_data['role'] = 'student'

        form = AccountRequestAdminForm(data=form_data,instance=ar)
        self.assertTrue(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_approval_account_exists(self,mock_get):
        ar = AccountRequest.objects.create(**self.ar_dict)
        form_data = copy.deepcopy(self.ar_dict)
        form_data['status'] = 'a'

        form = AccountRequestAdminForm(data=form_data,instance=ar)
        self.assertFalse(form.is_valid())

class AccountRequestFormRcLdapTestCase(LdapTestCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_user_exists(self,mock_get,mock_auth):
        form_data = {
            'organization': 'ucb',
            'username': 'testuser',
            'password': 'testpass',
        }
        form = AccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_accountrequest_exists(self,mock_get,mock_auth):
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
class SponsoredAccountRequestFormTestCase(LdapTestCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_valid(self,mock_get,mock_auth):
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

    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_missing_fields(self,mock_get,mock_auth):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = SponsoredAccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

# This test case covers the functionality of the class account request form
# delivered to the user during account request.
class ClassAccountRequestFormTestCase(LdapTestCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_valid(self,mock_get,mock_auth):
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

    @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
    def test_form_invalid_missing_fields(self,mock_get,mock_auth):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = ClassAccountRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

# This test case covers the functionality of the project account request form
# delivered to the user during account request.
# class ProjectAccountRequestFormTestCase(LdapTestCase):
#     def setUp(self):
#         proj_dict = {
#             'pi_emails': ['testpiuser@test.org'],
#             'managers': ['testpiuser'],
#             'collaborators': ['testpiuser'],
#             'organization': 'ucb',
#             'project_id': 'ucb1',
#             'title': 'Test project',
#             'description': 'Test project.',
#         }
#         Project.objects.create(**proj_dict)
#         proj_dict.update({
#             'project_id': 'ucb2',
#             'title': 'Test project 2',
#             'description': 'Test project 2.',
#         })
#         Project.objects.create(**proj_dict)
#         super(ProjectAccountRequestFormTestCase,self).setUp()
#
#     @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
#     @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
#     def test_form_valid(self,mock_get,mock_auth):
#         form_data = {
#             'projects': [proj.pk for proj in Project.objects.all()],
#             'organization': 'ucb',
#             'username': 'testuser',
#             'password': 'testpass',
#             'role': 'student',
#             'login_shell': '/bin/bash',
#         }
#         form = ProjectAccountRequestForm(data=form_data)
#         self.assertTrue(form.is_valid())
#
#     @mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True)
#     @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user)
#     def test_form_valid_missing_fields(self,mock_get,mock_auth):
#         form_data = {
#             'organization': 'ucb',
#             'username': 'testuser',
#             'password': 'testpass',
#             'role': 'student',
#             'login_shell': '/bin/bash',
#         }
#         form = ProjectAccountRequestForm(data=form_data)
#         self.assertFalse(form.is_valid())
