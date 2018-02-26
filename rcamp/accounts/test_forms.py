from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import pam
import copy

from django.conf import settings
from lib.test.ldap import (
    LdapTestCase,
    build_mock_rcldap_user
)

from accounts.forms import (
    AccountRequestVerifyUcbForm,
    AccountRequestVerifyCsuForm,
)
from accounts.admin import AccountRequestAdminForm
from accounts.models import (
    CuLdapUser,
    CsuLdapUser,
    AccountRequest,
    Intent
)


mock_cu_user_defaults = dict(
    username = 'testuser',
    first_name = 'Test',
    last_name = 'User',
    email = 'testuser@test.org',
    edu_affiliation = 'faculty'
)
mock_csu_user_defaults = dict(
    username = 'testuser',
    first_name = 'Test',
    last_name = 'User',
    email = 'testuser@test.org',
)
# TODO: Remove these declarations after the remaining tests have been updated
mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
mock_csu_user = mock.MagicMock(**mock_cu_user_defaults)

class AccountRequestVerifyUcbFormTestCase(LdapTestCase):
    def test_form_valid(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            self.assertTrue(form.is_valid())

    def test_form_invalid_bad_user(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        form_data = {
            'username': 'wronguser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',side_effect=[CuLdapUser.DoesNotExist]):
            self.assertFalse(form.is_valid())

    def test_form_invalid_bad_password(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = False
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            self.assertFalse(form.is_valid())

    def test_form_invalid_missing_fields(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        form_data = {
            'username': 'testuser',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            self.assertFalse(form.is_valid())

        form_data = {
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            self.assertFalse(form.is_valid())

        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            self.assertFalse(form.is_valid())


class AccountRequestVerifyCsuFormTestCase(LdapTestCase):
    def test_csu_form_valid(self):
        mock_csu_user = mock.MagicMock(**mock_csu_user_defaults)
        mock_csu_user.authenticate.return_value = True
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyCsuForm(data=form_data)
        with mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user):
            self.assertTrue(form.is_valid())

    def test_csu_form_invalid_bad_creds(self):
        mock_csu_user = mock.MagicMock(**mock_csu_user_defaults)
        mock_csu_user.authenticate.return_value = False
        form_data = {
            'username': 'wronguser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyCsuForm(data=form_data)
        with mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user):
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

    @mock.patch('accounts.models.RcLdapUser.objects.filter',return_value=[build_mock_rcldap_user(organization='ucb')])
    def test_form_invalid_approval_account_exists(self,mock_get):
        ar = AccountRequest.objects.create(**self.ar_dict)
        form_data = copy.deepcopy(self.ar_dict)
        form_data['username'] = 'testuser'
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
