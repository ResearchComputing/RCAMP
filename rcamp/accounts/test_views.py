from django.test import (
    TestCase,
    override_settings,
    RequestFactory
)
from django.http import Http404
from mock import MagicMock
import mock
import datetime

from django.conf import settings

from lib.test.utils import SafeTestCase
from lib.test.functional import SafeStaticLiveServerTestCase

from accounts.test_forms import CuBaseCase
from accounts.views import (
    ReasonView,
    AccountRequestReviewView,
    AccountRequestCreateView,
    SponsoredAccountRequestCreateView,
    ClassAccountRequestCreateView,
    ProjectAccountRequestCreateView
)
from accounts.models import (
    AccountRequest,
    IdTracker
)
from projects.models import Project



# Adds method for returning Class-Based View instance, so that
# methods can be individually tested.
class CbvCase(SafeTestCase):
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

# This test case covers the general account request page.
class AccountRequestTestCase(CuBaseCase,CbvCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create_csu(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/general',
                data={
                    'organization':'csu',
                    'username':'testuser',
                    'password':'testpass',
                    'login_shell': '/bin/bash',
                    'role': 'faculty',
                    'summit':True,
                    'petalibrary_archive':True,
                }
            )

        from accounts.models import CuLdapUser
        user = CuLdapUser.objects.get(username='testuser')
        with mock.patch('accounts.models.CsuLdapUser.objects.get',MagicMock(return_value=user)):
            with mock.patch('accounts.models.RcLdapUser.objects.create_user_from_request',MagicMock(return_value=True)):
                view = AccountRequestCreateView.as_view()
                response = view(request)

                self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

                ar = AccountRequest.objects.get(username='testuser')
                self.assertEquals(ar.status,'a')

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create_missing_username(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/general',
                data={
                    'organization':'ucb',
                    'username':'wronguser',
                    'password':'testpass'
                }
            )
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

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=False))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create_invalid_creds(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/ucb',
                data={
                    'organization':'ucb',
                    'username':'testuser',
                    'password':'testpass'
                }
            )
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
class SponsoredAccountRequestTestCase(CuBaseCase,CbvCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/sponsored',
                data={
                    'username':'testuser',
                    'password':'testpass',
                    'login_shell': '/bin/bash',
                    'sponsor_email': 'sponsor@colorado.edu',
                    'summit':True,
                    'petalibrary_archive':True,
                }
            )
        view = SponsoredAccountRequestCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.first_name,'test')
        self.assertEquals(ar.last_name,'user')
        self.assertEquals(ar.email,'testuser@test.org')
        self.assertEquals(ar.role, 'sponsored')
        self.assertEquals(ar.sponsor_email, 'sponsor@colorado.edu')
        self.assertEquals(ar.login_shell,'/bin/bash')
        self.assertEquals(ar.resources_requested,'summit,petalibrary_archive')
        self.assertEquals(ar.organization,'ucb')


#This test case covers the class account request page.
class ClassAccountRequestTestCase(CuBaseCase,CbvCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/class',
                data={
                    'username':'testuser',
                    'password':'testpass',
                    'login_shell': '/bin/bash',
                    'course_number': 'CSCI4000',
                }
            )
        view = ClassAccountRequestCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.first_name,'test')
        self.assertEquals(ar.last_name,'user')
        self.assertEquals(ar.email,'testuser@test.org')
        self.assertEquals(ar.role, 'student')
        self.assertEquals(ar.course_number, 'CSCI4000')
        self.assertEquals(ar.login_shell,'/bin/bash')
        self.assertEquals(ar.organization,'ucb')

#This test case covers the project account request page.
class ProjectAccountRequestTestCase(CuBaseCase,CbvCase):
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
        super(ProjectAccountRequestTestCase,self).setUp()

    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_request_create(self):
        request = RequestFactory().post(
                '/accounts/account-request/create/project',
                data={
                    'projects': [proj.pk for proj in Project.objects.all()],
                    'organization':'ucb',
                    'username':'testuser',
                    'password':'testpass',
                    'login_shell': '/bin/bash',
                    'role': 'student',
                }
            )
        view = ProjectAccountRequestCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/accounts/account-request/review/'))

        ar = AccountRequest.objects.get(username='testuser')
        ar_list = [p.pk for p in ar.projects.all()]
        expected_list = [p.pk for p in Project.objects.all()]
        self.assertEquals(ar_list,expected_list)
        self.assertEquals(ar.first_name,'test')
        self.assertEquals(ar.last_name,'user')
        self.assertEquals(ar.email,'testuser@test.org')
        self.assertEquals(ar.role, 'student')
        self.assertEquals(ar.login_shell,'/bin/bash')
        self.assertEquals(ar.organization,'ucb')
