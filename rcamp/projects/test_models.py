from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import copy
import datetime

from django.conf import settings

from projects.models import Project



class ProjectTestCase(TestCase):
    def setUp(self):
        self.proj_dict = {
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        }
        self.proj1 = Project.objects.create(**self.proj_dict)
        self.proj_dict.update({'project_id':'ucb3'})
        self.proj2 = Project.objects.create(**self.proj_dict)

    def test_create_project_no_id(self):
        proj_dict = copy.deepcopy(self.proj_dict)
        del proj_dict['project_id']
        proj = Project.objects.create(**proj_dict)

        self.assertEqual(proj.project_id,'ucb4')

    def test_create_project_id_multi_digit(self):
        self.proj1.project_id = 'ucb10'
        self.proj1.save()

        proj_dict = copy.deepcopy(self.proj_dict)
        del proj_dict['project_id']
        proj = Project.objects.create(**proj_dict)

        self.assertEqual(proj.project_id,'ucb11')
