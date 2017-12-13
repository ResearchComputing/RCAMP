from django.test import (
    TestCase,
    override_settings,
    RequestFactory
)
from django.http import Http404
import mock
import datetime

from django.conf import settings

from lib.test.ldap import LdapTestCase

from accounts.views import (
    ReasonView,
    AccountRequestReviewView,
    AccountRequestCreateView,
    SponsoredAccountRequestCreateView,
    ClassAccountRequestCreateView
)
from accounts.models import (
    AccountRequest,
    IdTracker,
    CuLdapUser
)



# Adds method for returning Class-Based View instance, so that
# methods can be individually tested.
class CbvCase(LdapTestCase):
    @staticmethod
    def setup_view(view,request,*args,**kwargs):
        # Mimic as_view() returned callable, but returns view instance.
        # args and kwargs are the same you would pass to ``reverse()``
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

# This test case covers the reason select page in the account
# request process.
class ReasonTestCase(CbvCase):
    def test_get(self):
        request = RequestFactory().get('/accounts/account-request/create')
        view = ReasonView()
        view = ReasonTestCase.setup_view(view,request)
        context = view.get_context_data()

        self.assertIsNotNone(context)

def get_account_request_defaults():
    """Returns reasonable defaults for account request POST data."""
    account_request_defaults = dict(
        organization = 'ucb',
        username = 'testuser',
        password = 'testpass',
        login_shell = '/bin/bash',
        role = 'faculty',
        summit = True,
        petalibrary_archive = True
    )
    return account_request_defaults

def get_org_user_defaults():
    """Returns a dictionary of reasonable defaults for users returned from external LDAPs."""
    defaults = dict(
        username = 'testuser',
        first_name = 'Test',
        last_name = 'User',
        email = 'testuser@colorado.edu'
    )
    return defaults

# This test case covers the account request review page.
class AccountRequestReviewTestCase(CbvCase):
    def setUp(self):
        super(AccountRequestReviewTestCase,self).setUp()
        self.ar_dict = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'tu@tu.org',
            'role': 'faculty',
            'organization': 'ucb'
        }
        ar = AccountRequest.objects.create(**self.ar_dict)

    def test_get(self):
        ar = AccountRequest.objects.get()
        request = RequestFactory().get('/accounts/account-request/review/%s'%ar.id)
        view = AccountRequestReviewView()
        view = AccountRequestReviewTestCase.setup_view(view,request,request_id=ar.id)
        context = view.get_context_data(request_id=ar.id)
        self.assertEquals(context['account_request'],ar)

    def test_get_invalid(self):
        request = RequestFactory().get('/accounts/account-request/review/1010101')
        view = AccountRequestReviewView()
        view = AccountRequestReviewTestCase.setup_view(view,request,request_id=1010101)
        self.assertRaises(Http404,view.get_context_data,**{'request_id':1010101})

# This test case covers the general account request page.
class AccountRequestTestCase(CbvCase):
    def setUp(self):
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )

    def test_request_create_csu(self):
        mock_csu_user_defaults = get_org_user_defaults()
        mock_csu_user = mock.MagicMock(**mock_csu_user_defaults)
        account_request_defaults = get_account_request_defaults()
        account_request_defaults['organization'] = 'csu'
        request = RequestFactory().post(
                '/accounts/account-request/create/general',
                data=account_request_defaults
            )

        with mock.patch('accounts.models.CsuLdapUser.objects.get',return_value=mock_csu_user):
            with mock.patch('accounts.models.CsuLdapUser.authenticate',return_value=True):
                view = AccountRequestCreateView.as_view()
                response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        # Auto-approve CSU requests
        self.assertEquals(ar.status,'a')

    def test_request_create_missing_username(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/general',
                data={
                    'organization':'ucb',
                    'username':'wronguser',
                    'password':'testpass'
                }
            )
        with mock.patch('accounts.models.CuLdapUser.objects.get',side_effect=[CuLdapUser.DoesNotExist]):
            with mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True):
                view = AccountRequestCreateView.as_view()
                response = view(request)

        self.assertEquals(
                response.context_data['form'].errors['__all__'],
                [u'Invalid username']
            )

        self.assertRaises(
                AccountRequest.DoesNotExist,
                AccountRequest.objects.get,
                **{'username':'wronguser'}
            )

    def test_request_create_invalid_creds(self):
        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        mock_cu_user.authenticate.return_value = False
        account_request_defaults = get_account_request_defaults()
        request = RequestFactory().post(
                '/accounts/account-request/create/ucb',
                data=account_request_defaults
            )

        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            view = AccountRequestCreateView.as_view()
            response = view(request)

        self.assertEquals(
                response.context_data['form'].errors['__all__'],
                [u'Invalid password']
            )

        self.assertRaises(
                AccountRequest.DoesNotExist,
                AccountRequest.objects.get,
                **{'username':'testuser'}
            )

#This test case covers the sponsored account request page.
class SponsoredAccountRequestTestCase(CbvCase):
    def test_request_create(self):
        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        account_request_defaults = get_account_request_defaults()
        account_request_defaults['sponsor_email'] = 'sponsor@colorado.edu'
        request = RequestFactory().post(
                '/accounts/account-request/create/sponsored',
                data=account_request_defaults
            )

        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            with mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True):
                view = SponsoredAccountRequestCreateView.as_view()
                response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.first_name,'Test')
        self.assertEquals(ar.last_name,'User')
        self.assertEquals(ar.email,'testuser@colorado.edu')
        self.assertEquals(ar.role, 'sponsored')
        self.assertEquals(ar.sponsor_email, 'sponsor@colorado.edu')
        self.assertEquals(ar.login_shell,'/bin/bash')
        self.assertEquals(ar.resources_requested,'summit,petalibrary_archive')
        self.assertEquals(ar.organization,'ucb')


#This test case covers the class account request page.
class ClassAccountRequestTestCase(CbvCase):
    def test_request_create(self):
        mock_cu_user_defaults = get_org_user_defaults()
        mock_cu_user = mock.MagicMock(**mock_cu_user_defaults)
        account_request_defaults = get_account_request_defaults()
        account_request_defaults['course_number'] = 'CSCI4000'
        request = RequestFactory().post(
                '/accounts/account-request/create/class',
                data=account_request_defaults
            )
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            with mock.patch('accounts.models.CuLdapUser.authenticate',return_value=True):
                view = ClassAccountRequestCreateView.as_view()
                response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.role, 'student')
        self.assertEquals(ar.course_number, 'CSCI4000')
        self.assertEquals(ar.login_shell,'/bin/bash')
        self.assertEquals(ar.organization,'ucb')
