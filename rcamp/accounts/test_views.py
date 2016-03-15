from django.test import TestCase
from django.test import override_settings
from django.test import RequestFactory
from django.http import Http404
from mock import MagicMock
import mock
import datetime

from django.conf import settings

from accounts.test_forms import CuBaseCase
from accounts.views import ReasonView
from accounts.views import AccountRequestReviewView
from accounts.views import CuAccountRequestCreateView
from accounts.models import AccountRequest


# Adds method for returning Class-Based View instance, so that
# methods can be individually tested.
class CbvCase(TestCase):
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

# This test case covers the CU account request page.
class CuAccountRequestTestCase(CuBaseCase,CbvCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/ucb',
                data={
                    'username':'testuser',
                    'password':'testpass',
                    'login_shell': '/bin/bash',
                    'role': 'faculty',
                    'summit':True,
                    'petalibrary_archive':True,
                }
            )
        view = CuAccountRequestCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.first_name,'test')
        self.assertEquals(ar.last_name,'user')
        self.assertEquals(ar.email,'testuser@test.org')
        self.assertEquals(ar.role, 'faculty')
        self.assertEquals(ar.login_shell,'/bin/bash')
        self.assertEquals(ar.resources_requested,'summit,petalibrary_archive')
        self.assertEquals(ar.organization,'ucb')

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create_missing_username(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/ucb',
                data={'username':'wronguser','password':'testpass'}
            )
        view = CuAccountRequestCreateView.as_view()
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

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=False))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create_invalid_creds(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/ucb',
                data={'username':'testuser','password':'testpass'}
            )
        view = CuAccountRequestCreateView.as_view()
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
