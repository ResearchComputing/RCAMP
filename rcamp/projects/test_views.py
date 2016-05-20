from django.test import TestCase
from django.test import RequestFactory
from django.test import override_settings

from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from accounts.test_models import BaseCase
from accounts.test_views import CbvCase
from projects.models import Project
from projects.models import Reference
from projects.views import ProjectListView
from projects.views import ProjectCreateView
from projects.views import ProjectEditView
from projects.views import ReferenceCreateView
from projects.views import ReferenceEditView


# This test case covers the project list view.
class ProjectListTestCase(CbvCase):
    def setUp(self):
        user_dict = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@test.org',
        }
        User.objects.create(**user_dict)
        proj_dict = {
            'pi_emails': ['testuser@test.org'],
            'managers': ['testuser'],
            'collaborators': ['testuser'],
            'organization': 'ucb',
            'project_id': 'ucb1',
            'title': 'Test project',
            'description': 'Test project.',
        }
        Project.objects.create(**proj_dict)
        super(ProjectListTestCase,self).setUp()

    def test_get(self):
        request = RequestFactory().get('/projects/list')
        request.user = User.objects.get()
        view = ProjectListView()
        view = ProjectListTestCase.setup_view(view,request)
        queryset = view.get_queryset()

        test_queryset = Project.objects.filter(project_id='ucb1')
        self.assertEqual(queryset.count(), test_queryset.count())

    def test_get_unauthed(self):
        response = self.client.get('/projects/list')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login?next=/projects/list'))

# This test case covers the project creation page.
class ProjectCreateTestCase(BaseCase,CbvCase):
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
                    'pi_emails': 'testuser@test.org,cuuser@cu.edu',
                    'managers': ['testuser','testcuuser'],
                    'collaborators': ['testuser','testcuuser'],
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
        self.assertEquals(proj.managers,['testuser','testcuuser','testrequester'])
        self.assertEquals(proj.collaborators,['testuser','testcuuser'])
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

# This test case covers the project edit page.
class ProjectEditTestCase(BaseCase,CbvCase):
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

        self.assertTrue(response.url.startswith('/projects/list/{}/'.format(self.proj.pk)))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project Updated')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu','test@test.org'])
        self.assertEquals(proj.managers,['testcuuser','testrequester','testuser'])
        self.assertEquals(proj.collaborators,['testuser','testcuuser'])
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
