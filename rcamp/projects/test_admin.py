from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import copy
import pytz

from django.conf import settings
from accounts.test_admin import AdminTestCase
from projects.models import Project
from projects.models import Allocation



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
                'allocation_set-TOTAL_FORMS': '0',
                'allocation_set-INITIAL_FORMS': '0',
                'allocation_set-MIN_NUM_FORMS': '0',
                'allocation_set-MAX_NUM_FORMS': '0',
                'allocationrequest_set-TOTAL_FORMS': '0',
                'allocationrequest_set-INITIAL_FORMS': '0',
                'allocationrequest_set-MIN_NUM_FORMS': '0',
                'allocationrequest_set-MAX_NUM_FORMS': '0',
                # 'allocations-project': '',
                # 'allocations-allocation_id': '',
                # 'allocations-amount': '',
                # 'allocations-start_date': '',
                # 'allocations-end_date': '',
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
                'allocation_set-TOTAL_FORMS': '0',
                'allocation_set-INITIAL_FORMS': '0',
                'allocation_set-MIN_NUM_FORMS': '0',
                'allocation_set-MAX_NUM_FORMS': '0',
                'allocationrequest_set-TOTAL_FORMS': '0',
                'allocationrequest_set-INITIAL_FORMS': '0',
                'allocationrequest_set-MIN_NUM_FORMS': '0',
                'allocationrequest_set-MAX_NUM_FORMS': '0',
                # 'allocations-project': '',
                # 'allocations-allocation_id': '',
                # 'allocations-amount': '',
                # 'allocations-start_date': '',
                # 'allocations-end_date': '',
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

class AllocationsAdminTestCase(AdminTestCase):
    def test_index(self):
        response = self.client.get('/admin/projects/')
        self.assertContains(response, "Allocations")

class AdminAllocationTestCase(AllocationsAdminTestCase):
    def setUp(self):
        self.test_proj = Project.objects.create(**{
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,02,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)
        self.test_alloc = Allocation.objects.create(**{
            'project': self.test_proj,
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
        })
        super(AdminAllocationTestCase,self).setUp()

    def test_allocation_list(self):
        response = self.client.get('/admin/projects/allocation/')
        self.assertContains(response, "Allocations")
        self.assertContains(response, "ucb1_summit1")
        self.assertContains(response, "50000")

    def test_allocation_detail(self):
        response = self.client.get(
            '/admin/projects/allocation/{}/'.format(self.test_alloc.pk)
        )
        self.assertContains(response, "ucb1_summit1")
        self.assertContains(response, "50000")
        self.assertContains(response, "2016-02-02")
        self.assertContains(response, "2017-02-02")

    def test_allocation_add(self):
        response = self.client.post(
            '/admin/projects/allocation/add/',
            {
                'project': self.test_proj.pk,
                'amount': '50000',
                'start_date': '2016-02-02',
                'end_date': '2017-02-02',
            }
        )
        self.assertRedirects(response, '/admin/projects/allocation/')
        alloc = Allocation.objects.get(allocation_id='ucb1_summit2')
        self.assertEquals(alloc.amount,50000)
