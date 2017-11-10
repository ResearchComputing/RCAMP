from django.test import RequestFactory
from django.test import override_settings

from django.http.response import HttpResponseRedirect

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from lib.test.ldap import (
    LdapTestCase,
    get_ldap_user_defaults
)
from projects.models import (
    Project,
    Reference,
    AllocationRequest
)
from projects.forms import RcLdapUser
from projects.views import (
    ProjectListView,
    ProjectCreateView,
    ProjectEditView,
    ReferenceCreateView,
    ReferenceEditView,
    AllocationRequestCreateView
)

import mock
from unittest import skip


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

class RcLdapUserMock (object):
    def __init__ (self, dn, username, first_name, last_name, organization):
        self.dn = dn
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.organization = organization


class RcLdapUserQuerySet (object):
    order_by = mock.MagicMock(return_value=[
        RcLdapUserMock('uid=testuser,ou=ucb,dc=admin,dc=org', 'testuser', 'Test', 'User','ou=ucb'),
        RcLdapUserMock('uid=testcuuser,ou=ucb,dc=admin,dc=org', 'testcuuser', 'Test', 'CUUser','ou=ucb'),
        RcLdapUserMock('uid=testrequester,ou=ucb,dc=admin,dc=org', 'testrequester', 'Test', 'Requester','ou=ucb'),
        RcLdapUserMock('uid=testcsurequester,ou=csu,dc=admin,dc=org', 'testcsurequester', 'Test', 'Requester','ou=csu'),
    ])


class RcLdapUserObjectManager (object):
    all = mock.MagicMock(return_value=RcLdapUserQuerySet())

@skip("Functional tests will deprecate.")
# This test case covers the project creation page.
@mock.patch.object(RcLdapUser, 'objects', RcLdapUserObjectManager)
class ProjectCreateTestCase(CbvCase):
    def setUp(self):
        super(ProjectCreateTestCase,self).setUp()
        self.user = User.objects.create(**{
            'username': 'testrequester',
            'email': 'testr@test.org',
            'first_name': 'Test',
            'last_name': 'Requester',
        })

    def test_get_unauthed(self):
        response = self.client.get('/projects/create')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login?next=/projects/create'))

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_create(self):
        request = RequestFactory().post(
                '/projects/create',
                data={
                    'project_id': 'ucb1',
                    'title': 'Test Project',
                    'description': 'A test project',
                    'pi_emails': 'testuser@test.org, cuuser@cu.edu',
                    'managers': ['uid=testuser,ou=ucb,dc=admin,dc=org','uid=testcuuser,ou=ucb,dc=admin,dc=org'],
                    'collaborators': ['uid=testuser,ou=ucb,dc=admin,dc=org','uid=testcuuser,ou=ucb,dc=admin,dc=org'],
                    'organization':'ucb',
                }
            )
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/projects/list/'))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu'])
        self.assertEquals(proj.managers,['uid=testuser,ou=ucb,dc=admin,dc=org','uid=testcuuser,ou=ucb,dc=admin,dc=org','uid=testrequester,ou=ucb,dc=admin,dc=org'])
        self.assertEquals(proj.collaborators,['uid=testuser,ou=ucb,dc=admin,dc=org','uid=testcuuser,ou=ucb,dc=admin,dc=org'])
        self.assertEquals(proj.organization,'ucb')

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_create_missing_coll_man(self):
        request = RequestFactory().post(
                '/projects/create',
                data={
                    'project_id': 'ucb1',
                    'title': 'Test Project',
                    'description': 'A test project',
                    'pi_emails': 'testuser@test.org,cuuser@cu.edu',
                    'organization':'ucb',
                }
            )
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)

        self.assertIs(response.__class__, HttpResponseRedirect)
        self.assertTrue(response.url.startswith('/projects/list/'))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu'])
        self.assertEquals(proj.managers,[u'testrequester'])
        self.assertEquals(proj.collaborators,[])
        self.assertEquals(proj.organization,'ucb')

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_create_no_project_id(self):
        data = {
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': 'testuser@test.org,cuuser@cu.edu',
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        }

        request = RequestFactory().post('/projects/create',data)
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)
        self.assertTrue(response.url.startswith('/projects/list/'))
        proj = Project.objects.filter(project_id='ucb1')
        self.assertEqual(proj.count(),1)

        request = RequestFactory().post('/projects/create',data)
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)
        self.assertTrue(response.url.startswith('/projects/list/'))
        proj = Project.objects.filter(project_id='ucb2')
        self.assertEqual(proj.count(),1)

        data.update({'organization':'csu'})
        request = RequestFactory().post('/projects/create',data)
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)
        self.assertTrue(response.url.startswith('/projects/list/'))
        proj = Project.objects.filter(project_id='ucb1')
        self.assertEqual(proj.count(),1)

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_create_missing_pi_emails(self):
        request = RequestFactory().post(
                '/projects/create',
                data = {
                    'title': 'Test Project',
                    'description': 'A test project',
                    'managers': ['testuser','testcuuser'],
                    'collaborators': ['testuser','testcuuser'],
                    'organization':'ucb',
                }
            )
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)

        self.assertEquals(
                len(response.context_data['form'].errors['pi_emails']),
                1
            )

        self.assertRaises(
                Project.DoesNotExist,
                Project.objects.get,
                **{}
            )

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_create_missing_explanation(self):
        request = RequestFactory().post(
                '/projects/create',
                data = {
                    # 'title': 'Test Project',
                    # 'description': 'A test project',
                    'pi_emails': 'testuser@test.org,cuuser@cu.edu',
                    'managers': ['testuser','testcuuser'],
                    'collaborators': ['testuser','testcuuser'],
                    'organization':'ucb',
                }
            )
        request.user = self.user
        view = ProjectCreateView.as_view()
        response = view(request)

        self.assertEquals(
                len(response.context_data['form'].errors['title']),
                1
            )
        self.assertEquals(
                len(response.context_data['form'].errors['description']),
                1
            )

        self.assertRaises(
                Project.DoesNotExist,
                Project.objects.get,
                **{}
            )

@skip("Functional tests will deprecate.")
# This test case covers the project edit page.
@mock.patch.object(RcLdapUser, 'objects', RcLdapUserObjectManager)
class ProjectEditTestCase(CbvCase):
    def setUp(self):
        super(ProjectEditTestCase,self).setUp()
        self.user = User.objects.create(**{
            'username': 'testuser',
            'email': 'testr@test.org',
            'first_name': 'Test',
            'last_name': 'Requester',
        })
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })

    def test_get_unauthed(self):
        response = self.client.get('/projects/list/{}/edit'.format(self.proj.pk))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login?next=/projects/' in response.url)

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_update(self):
        request = RequestFactory().post(
                '/projects/list/{}/edit'.format(self.proj.pk),
                data={
                    'title': 'Test Project Updated',
                    'description': 'A test project',
                    'pi_emails': 'testuser@test.org,cuuser@cu.edu,test@test.org',
                    'managers': ['testuser','testcuuser','testrequester'],
                    'collaborators': ['testuser','testcuuser'],
                }
            )
        request.user = self.user
        view = ProjectEditView.as_view()
        response = view(request)

        self.assertIs(response.__class__, HttpResponseRedirect)
        self.assertTrue(response.url.startswith('/projects/list/{}/'.format(self.proj.pk)))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project Updated')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu','test@test.org'])
        self.assertEquals(proj.managers,['testuser','testcuuser','testrequester'])
        self.assertEquals(proj.collaborators,['testuser','testcuuser'])
        self.assertEquals(proj.organization,'ucb')

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_update_removed_self(self):
        request = RequestFactory().post(
                '/projects/list/{}/edit'.format(self.proj.pk),
                data={
                    'title': 'Test Project Updated',
                    'description': 'A test project',
                    'pi_emails': 'testuser@test.org,cuuser@cu.edu,test@test.org',
                    'managers': ['testcuuser','testrequester'],
                    'collaborators': ['testuser','testcuuser'],
                }
            )
        request.user = self.user
        view = ProjectEditView.as_view()
        response = view(request)

        self.assertIs(response.__class__, HttpResponseRedirect)
        self.assertTrue(response.url.startswith('/projects/list/{}/'.format(self.proj.pk)))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project Updated')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu','test@test.org'])
        self.assertEquals(proj.managers,['testcuuser','testrequester','testuser'])
        self.assertEquals(proj.collaborators,['testuser','testcuuser'])
        self.assertEquals(proj.organization,'ucb')

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_update_no_coll_man(self):
        request = RequestFactory().post(
                '/projects/list/{}/edit'.format(self.proj.pk),
                data={
                    'title': 'Test Project Updated',
                    'description': 'A test project',
                    'pi_emails': 'testuser@test.org,cuuser@cu.edu,test@test.org',
                }
            )
        request.user = self.user
        view = ProjectEditView.as_view()
        response = view(request)

        self.assertIs(response.__class__, HttpResponseRedirect)
        self.assertTrue(response.url.startswith('/projects/list/{}/'.format(self.proj.pk)))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project Updated')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu','test@test.org'])
        self.assertEquals(proj.managers,[u'testuser'])
        self.assertEquals(proj.collaborators,[])
        self.assertEquals(proj.organization,'ucb')

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_update_missing_fields(self):
        request = RequestFactory().post(
                '/projects/list/{}/edit'.format(self.proj.pk),
                data={
                    'managers': ['testcuuser','testrequester'],
                    'collaborators': ['testuser','testcuuser'],
                }
            )
        request.user = self.user
        view = ProjectEditView.as_view()
        response = view(request)

        self.assertEquals(
                response.context_data['form'].errors['title'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['description'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['pi_emails'],
                [u'This field is required.']
            )

@skip("Functional tests will deprecate.")
# This test case covers the reference creation page.
class ReferenceCreateTestCase(CbvCase):
    def setUp(self):
        super(ReferenceCreateTestCase,self).setUp()
        self.user = User.objects.create(**{
            'username': 'testuser',
            'email': 'testr@test.org',
            'first_name': 'Test',
            'last_name': 'Requester',
        })
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })

    def test_reference_create(self):

        request = RequestFactory().post(
                '/projects/{}/references/create'.format(self.proj.pk),
                data={
                    'description': 'A reference.',
                    'link': 'A link',
                }
            )
        request.user = self.user
        view = ReferenceCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/projects/list/{}/references/'.format(self.proj.pk)))

        ref = Reference.objects.get(pk=1)
        self.assertEquals(ref.project.project_id,self.proj.project_id)
        self.assertEquals(ref.description,'A reference.')
        self.assertEquals(ref.link,'A link')

    def test_reference_create_missing_fields(self):
        request = RequestFactory().post(
                '/projects/list/{}/references/create'.format(self.proj.pk),
                data={}
            )
        request.user = self.user
        view = ReferenceCreateView.as_view()
        response = view(request)

        self.assertEquals(
                response.context_data['form'].errors['description'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['link'],
                [u'This field is required.']
            )

@skip("Functional tests will deprecate.")
# This test case covers the reference edit page.
class ReferenceEditTestCase(CbvCase):
    def setUp(self):
        super(ReferenceEditTestCase,self).setUp()
        self.user = User.objects.create(**{
            'username': 'testuser',
            'email': 'testr@test.org',
            'first_name': 'Test',
            'last_name': 'Requester',
        })
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })
        self.ref = Reference.objects.create(**{
            'project': self.proj,
            'description': 'A reference.',
            'link': 'A link',
        })

    def test_reference_update(self):
        request = RequestFactory().post(
                '/projects/list/{}/references/{}/edit'.format(self.proj.pk,self.ref.pk),
                data={
                    'description': 'An updated reference.',
                    'link': 'A link',
                }
            )
        request.user = self.user
        view = ReferenceEditView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/projects/list/{}/references/{}/'.format(self.proj.pk,self.ref.pk)))

        ref = Reference.objects.get(pk=self.ref.pk)
        self.assertEquals(ref.project.project_id,self.proj.project_id)
        self.assertEquals(ref.description,'An updated reference.')
        self.assertEquals(ref.link, 'A link')

    def test_reference_update_missing_fields(self):
        request = RequestFactory().post(
                '/projects/list/{}/references/{}/edit'.format(self.proj.pk,self.ref.pk),
                data={}
            )
        request.user = self.user
        view = ReferenceEditView.as_view()
        response = view(request)

        self.assertEquals(
                response.context_data['form'].errors['description'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['link'],
                [u'This field is required.']
            )

@skip("Functional tests will deprecate.")
# This test case covers the Allocation Request create page
class AllocationRequestCreateTestCase(CbvCase):
    def setUp(self):
        super(AllocationRequestCreateTestCase,self).setUp()
        self.user = User.objects.create(**{
            'username': 'testuser',
            'email': 'testr@test.org',
            'first_name': 'Test',
            'last_name': 'Requester',
        })
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })

    def test_allocationrequest_create(self):

        with ContentFile(b'content', name='plain.txt') as fp:
            request = RequestFactory().post(
                    '/projects/{}/allocationrequests/create'.format(self.proj.pk),
                    data={
                        'abstract': 'test abstract',
                        'funding': 'test funding',
                        'proposal': fp,
                        'time_requested': '1234',
                        'disk_space': '1234',
                        'software_request': 'none',
                    }
                )
            request.user = self.user
            view = AllocationRequestCreateView.as_view()
            response = view(request)

        self.assertTrue(response.url.startswith('/projects/list/{}/allocationrequests/'.format(self.proj.pk)))

        ar = AllocationRequest.objects.get()
        self.assertEquals(ar.project.project_id,self.proj.project_id)
        self.assertEquals(ar.abstract,'test abstract')
        self.assertEquals(ar.funding,'test funding')

        path_cmps = ar.proposal.name.split('/')
        self.assertEquals(len(path_cmps),5)
        self.assertEquals(path_cmps[-1][-3:],'txt')

        self.assertEquals(ar.time_requested,1234)
        self.assertEquals(ar.disk_space,1234)
        self.assertEquals(ar.software_request,'none')

        self.assertEquals(ar.requester,self.user.username)

    def test_allocationrequest_create_missing_fields(self):
        request = RequestFactory().post(
                '/projects/list/{}/allocationrequests/create'.format(self.proj.pk),
                data={}
            )
        request.user = self.user
        view = AllocationRequestCreateView.as_view()
        response = view(request)

        self.assertEquals(
                response.context_data['form'].errors['abstract'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['funding'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['proposal'],
                [u'This field is required.']
            )
        self.assertEquals(
                response.context_data['form'].errors['time_requested'],
                [u'This field is required.']
            )
