from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import pam
import copy

from django.conf import settings
from tests.utilities.ldap import (
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
    AccountRequest
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

    def test_form_invalid_user_exists(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
        }
        form = AccountRequestVerifyUcbForm(data=form_data)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user),mock.patch('accounts.models.RcLdapUser.objects.get_user_from_suffixed_username',return_value=mock_cu_user):
            self.assertFalse(form.is_valid())

    def test_form_invalid_accountrequest_exists(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        ar_dict = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'tu@tu.org',
            'organization': 'ucb',
            'role': 'faculty',
            'department': 'physics',
        }
        ar = AccountRequest.objects.create(**ar_dict)
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'faculty',
            'department': 'physics',
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
            'login_shell': '/bin/bash',
            'status': 'p'
        }

    def test_form_valid_create_approve_request(self):
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        form_data = {
            'organization': 'ucb',
            'username': 'newtestuser',
            'first_name': 'test',
            'last_name': 'user',
            'email': 'newtestuser@test.org',
            'role': 'faculty',
            'department': 'physics',
            'login_shell': '/bin/bash',
            'status': 'p'
        }
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            form = AccountRequestAdminForm(data=form_data)
            self.assertTrue(form.is_valid())

            ar = AccountRequest.objects.create(**form_data)
            form_data['status'] = 'a'

            form = AccountRequestAdminForm(data=form_data,instance=ar)
            self.assertTrue(form.is_valid())

    def test_form_valid_request_modified(self):
        ar = AccountRequest.objects.create(**self.ar_dict)
        form_data = copy.deepcopy(self.ar_dict)
        form_data['role'] = 'faculty'

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
