from django.test import TestCase
from django.test import RequestFactory

from django.contrib.auth.models import User
from accounts.test_views import CbvCase
from projects.models import Project
from projects.views import ProjectListView
from projects.views import ProjectCreateView



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

# This test case covers the project creation page.
class ProjectCreateTestCase(CbvCase):
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
        view = ProjectCreateView.as_view()
        response = view(request)

        self.assertTrue(response.url.startswith('/projects/list/'))

        proj = Project.objects.get(project_id='ucb1')
        self.assertEquals(proj.title,'Test Project')
        self.assertEquals(proj.description,'A test project')
        self.assertEquals(proj.pi_emails,['testuser@test.org','cuuser@cu.edu'])
        self.assertEquals(proj.managers,['testuser','testcuuser'])
        self.assertEquals(proj.collaborators,['testuser','testcuuser'])
        self.assertEquals(proj.organization,'ucb')

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
        view = ProjectCreateView.as_view()
        response = view(request)
        self.assertTrue(response.url.startswith('/projects/list/'))
        proj = Project.objects.filter(project_id='ucb1')
        self.assertEqual(proj.count(),1)

        request = RequestFactory().post('/projects/create',data)
        view = ProjectCreateView.as_view()
        response = view(request)
        self.assertTrue(response.url.startswith('/projects/list/'))
        proj = Project.objects.filter(project_id='ucb2')
        self.assertEqual(proj.count(),1)

        data.update({'organization':'csu'})
        request = RequestFactory().post('/projects/create',data)
        view = ProjectCreateView.as_view()
        response = view(request)
        self.assertTrue(response.url.startswith('/projects/list/'))
        proj = Project.objects.filter(project_id='ucb1')
        self.assertEqual(proj.count(),1)

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
