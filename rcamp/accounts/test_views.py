from django.test import (
    TestCase,
    override_settings,
    RequestFactory,
    Client
)
from django.http import Http404
import mock
import datetime

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware

from lib.test.ldap import LdapTestCase
from lib.test.utils import SessionEnabledTestMixin

from accounts.models import (
    AccountRequest,
    Intent,
    IdTracker,
    CuLdapUser,
    CsuLdapUser
)



def get_account_request_verify_defaults():
    """Returns reasonable defaults for account request verification step POST data."""
    verification_defaults = dict(
        username = 'testuser',
        password = 'testpass',
        role = 'faculty',
        department = 'physics'
    )
    return verification_defaults

def get_org_user_defaults():
    """Returns a dictionary of reasonable defaults for users returned from external LDAPs."""
    defaults = dict(
        username = 'testuser',
        first_name = 'Test',
        last_name = 'User',
        email = 'testuser@colorado.edu'
    )
    return defaults


class AccountRequestVerifyUcbViewTestCase(LdapTestCase):
    def test_request_verify(self):
        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        account_request_verify_defaults = get_account_request_verify_defaults()

        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            mock_cu_user.edu_affiliation = ['affiliated','unrecognized']
            response = self.client.post(
                    '/accounts/account-request/create/verify/ucb',
                    data=account_request_verify_defaults
                )
            session_ar_data = self.client.session['account_request_data']

            self.assertEquals(response.status_code, 302)
            self.assertTrue(response.url.endswith('/accounts/account-request/create/intent'))
            self.assertEquals(session_ar_data['organization'],'ucb')
            self.assertFalse('status' in session_ar_data)
            self.assertEquals(session_ar_data['email'],'testuser@colorado.edu')
            self.assertEquals(session_ar_data['role'],'faculty')
            self.assertEquals(session_ar_data['department'],'physics')
            self.assertEquals(session_ar_data['first_name'],'Test')
            self.assertEquals(session_ar_data['last_name'],'User')
            self.assertEquals(session_ar_data['username'],'testuser')

    def test_request_verify_autoapprove(self):
        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        account_request_verify_defaults = get_account_request_verify_defaults()

        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            mock_cu_user.edu_affiliation = ['faculty']
            response = self.client.post(
                    '/accounts/account-request/create/verify/ucb',
                    data=account_request_verify_defaults
                )
            session_ar_data = self.client.session['account_request_data']

            self.assertEquals(response.status_code, 302)
            self.assertTrue(response.url.endswith('/accounts/account-request/create/intent'))
            self.assertEquals(session_ar_data['organization'],'ucb')
            self.assertEquals(session_ar_data['status'],'a')

    def test_request_verify_invalid_creds(self):
        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = True
        account_request_verify_defaults = get_account_request_verify_defaults()

        with mock.patch('accounts.models.CuLdapUser.objects.get',side_effect=[CuLdapUser.DoesNotExist]):
            response = self.client.post(
                    '/accounts/account-request/create/verify/ucb',
                    data=account_request_verify_defaults
                )

            self.assertEquals(
                    response.context['form'].errors['__all__'],
                    [u'Invalid username']
                )
            self.assertRaises(
                    AccountRequest.DoesNotExist,
                    AccountRequest.objects.get,
                    **{'username':account_request_verify_defaults['username']}
                )

        mock_cu_user.authenticate.return_value = False
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            response = self.client.post(
                    '/accounts/account-request/create/verify/ucb',
                    data=account_request_verify_defaults
                )

            self.assertEquals(
                    response.context['form'].errors['__all__'],
                    [u'Invalid password']
                )
            self.assertRaises(
                    AccountRequest.DoesNotExist,
                    AccountRequest.objects.get,
                    **{'username':account_request_verify_defaults['username']}
                )


class AccountRequestVerifyCsuViewTestCase(LdapTestCase):
    def test_request_verify(self):
        mock_csu_user_defaults = get_org_user_defaults()
        mock_csu_user = mock.MagicMock(**mock_csu_user_defaults)
        mock_csu_user.authenticate.return_value = True
        account_request_verify_defaults = get_account_request_verify_defaults()

        with mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user):
            response = self.client.post(
                    '/accounts/account-request/create/verify/csu',
                    data=account_request_verify_defaults
                )
            session_ar_data = self.client.session['account_request_data']

            self.assertEquals(response.status_code, 302)
            self.assertTrue(response.url.endswith('/accounts/account-request/create/intent'))
            self.assertEquals(session_ar_data['organization'],'csu')
            self.assertEquals(session_ar_data['status'],'a')

    def test_request_verify_invalid_creds(self):
        mock_csu_user_defaults = get_org_user_defaults()
        mock_csu_user = mock.MagicMock(**mock_csu_user_defaults)
        mock_csu_user.authenticate.return_value = True
        account_request_verify_defaults = get_account_request_verify_defaults()

        with mock.patch('accounts.models.CsuLdapUser.objects.get',side_effect=[CsuLdapUser.DoesNotExist]):
            response = self.client.post(
                    '/accounts/account-request/create/verify/csu',
                    data=account_request_verify_defaults
                )

            self.assertEquals(
                    response.context['form'].errors['__all__'],
                    [u'Invalid username']
                )
            self.assertRaises(
                    AccountRequest.DoesNotExist,
                    AccountRequest.objects.get,
                    **{'username':account_request_verify_defaults['username']}
                )

        mock_csu_user.authenticate.return_value = False
        with mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user):
            response = self.client.post(
                    '/accounts/account-request/create/verify/csu',
                    data=account_request_verify_defaults
                )

            self.assertEquals(
                    response.context['form'].errors['__all__'],
                    [u'Invalid password']
                )
            self.assertRaises(
                    AccountRequest.DoesNotExist,
                    AccountRequest.objects.get,
                    **{'username':account_request_verify_defaults['username']}
                )


def get_account_request_session_defaults():
    """
    Returns reasonable defaults for account request data stored in session between verification and
    intent views.
    """
    session_request_defaults = dict(
        organization = 'ucb',
        username = 'testuser',
        email = 'testuser@colorado.edu',
        first_name = 'Test',
        last_name = 'User',
        role = 'faculty',
        department = 'physics'
    )
    return session_request_defaults


class AccountRequestIntentViewTestCase(LdapTestCase,SessionEnabledTestMixin):
    def setUp(self):
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )

    def test_request_submit_intent_summit(self):
        account_request_data = get_account_request_session_defaults()

        session = self.get_session(self.client)
        session['account_request_data'] = account_request_data
        session.save()

        intent_request_data = dict(
            reason_summit = True,
            additional_summit_description = 'Description of work.',
            additional_summit_funding = 'NSF Grant 1234'
        )
        response = self.client.post(
            '/accounts/account-request/create/intent',
            data = intent_request_data
        )
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response.url.endswith('/accounts/account-request/review'))

        account_request = AccountRequest.objects.get(username='testuser')
        self.assertEquals(self.client.session['account_request_data']['id'],account_request.id)

        intent = Intent.objects.get(account_request=account_request)
        self.assertEquals(intent.resources_requested,['summit'])
