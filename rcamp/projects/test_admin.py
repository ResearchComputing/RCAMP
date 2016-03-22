from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import copy

from django.conf import settings
from accounts.test_admin import AdminTestCase
from projects.models import Project



class ProjectsAdminTestCase(AdminTestCase):
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_index(self):
        response = self.client.get('/admin/projects/')
        self.assertContains(response, "Projects")

class AdminProjectTestCase(ProjectsAdminTestCase):
    def setUp(self):
        self.test_proj = Project.objects.create(**{
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })
        self.test_proj2 = Project.objects.create(**{
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })
        super(AdminProjectTestCase,self).setUp()

    def test_project_list(self):
        response = self.client.get('/admin/projects/project/')
        self.assertContains(response, "Projects")
        self.assertContains(response, "ucb1")
        self.assertContains(response, "testuser@test.org")

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_detail(self):
        response = self.client.get(
            '/admin/projects/project/{}/'.format(self.test_proj.pk)
        )
        self.assertContains(response, "Test Project")
        self.assertContains(response, "ucb1")
        self.assertContains(response, "testuser@test.org,cuuser@cu.edu")
        # Filter select field loaded:
        self.assertContains(response, "testuser")
        self.assertContains(response, "testcuuser")

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_add(self):
        response = self.client.post(
            '/admin/projects/project/add/',
            {
                'title': 'Test Project 2',
                'description': 'A second test project',
                'pi_emails': 'testuser@test.org,cuuser@cu.edu',
                'managers': ['testuser','testcuuser'],
                'collaborators': ['testuser','testcuuser'],
                'organization':'ucb',
            }
        )
        self.assertRedirects(response, '/admin/projects/project/')
        proj = Project.objects.get(project_id='ucb2')
        self.assertEquals(proj.managers,['testuser','testcuuser'])

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_modify(self):
        response = self.client.post(
            '/admin/projects/project/{}/'.format(self.test_proj2.pk),
            {
                'project_id': '',
                'title': 'Test Project',
                'description': 'A test project',
                'pi_emails': 'testuser@test.org,cuuser@cu.edu',
                'managers': ['testuser'],
                'collaborators': ['testuser','testcuuser'],
                'organization':'csu',
            }
        )
        self.assertRedirects(response, '/admin/projects/project/')
        proj = Project.objects.get(project_id='csu1')
        self.assertEquals(proj.managers,['testuser'])

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_project_delete(self):
        response = self.client.post(
            '/admin/projects/project/{}/delete/'.format(self.test_proj.pk),
            {'yes': 'post'}
        )
        self.assertRedirects(response, '/admin/projects/project/')
        qs = Project.objects.filter(project_id='ucb1')
        self.assertEquals(qs.count(), 0)
