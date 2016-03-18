from django.test import TestCase
from django.test import RequestFactory

from django.contrib.auth.models import User
from accounts.test_views import CbvCase
from projects.models import Project
from projects.views import ProjectListView



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
