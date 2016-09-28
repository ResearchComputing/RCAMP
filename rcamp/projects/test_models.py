from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import copy
import datetime
import pytz

from django.conf import settings

from projects.models import Project
from projects.models import Allocation
from projects.models import AllocationRequest



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

class AllocationTestCase(TestCase):
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
        self.proj = Project.objects.create(**self.proj_dict)

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,02,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)

        self.alloc_dict = {
            'project': self.proj,
            'allocation_id': 'ucb1_2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
        }
        self.alloc1 = Allocation.objects.create(**self.alloc_dict)

    def test_create_alloc_no_id(self):
        alloc_dict = copy.deepcopy(self.alloc_dict)
        del alloc_dict['allocation_id']
        alloc = Allocation.objects.create(**alloc_dict)

        self.assertEqual(alloc.allocation_id,'ucb1_3')

class AllocationCreateTestCase(TestCase):
    def setUp(self):
        super(AllocationCreateTestCase,self).setUp()
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })
        self.ar_dict = {
            'project': self.proj,
            'amount_awarded': 1234,
            'time_requested': 12345
        }

    def test_create_allocation_from_request(self):
        alloc = Allocation.objects.create_allocation_from_request(**self.ar_dict)

        self.assertEquals(alloc.project,self.proj)
        self.assertEquals(alloc.amount,self.ar_dict['amount_awarded'])
        self.assertIsNotNone(alloc.start_date)
        self.assertIsNotNone(alloc.end_date)

        tmp_dict = copy.deepcopy(self.ar_dict)
        del tmp_dict['amount_awarded']
        alloc = Allocation.objects.create_allocation_from_request(**tmp_dict)
        self.assertEquals(alloc.amount,self.ar_dict['time_requested'])

    def test_create_allocation_from_request_missing_fields(self):
        tmp_dict = copy.deepcopy(self.ar_dict)
        del tmp_dict['project']
        self.assertRaises(
                TypeError,
                Allocation.objects.create_allocation_from_request,
                **tmp_dict
            )
        tmp_dict = copy.deepcopy(self.ar_dict)
        del tmp_dict['amount_awarded']
        del tmp_dict['time_requested']
        self.assertRaises(
                TypeError,
                Allocation.objects.create_allocation_from_request,
                **tmp_dict
            )

# This test case covers AllocationRequest model functionality.
class AllocationRequestTestCase(TestCase):
    def setUp(self):
        super(AllocationRequestTestCase,self).setUp()
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'managers': ['testuser','testcuuser'],
            'collaborators': ['testuser','testcuuser'],
            'organization':'ucb',
        })
        self.ar_dict = {
            'project': self.proj,
            'abstract': 'test abstract',
            'funding': 'test funding',
            'time_requested': 1234,
            'amount_awarded': 0,
            'disk_space': 1234,
            'software_request': 'none',
            'requester': 'testuser',
        }
        ar = AllocationRequest.objects.create(**self.ar_dict)

    def test_loaded_values(self):
        ar = AllocationRequest.objects.get(project=self.proj)
        test_dict = copy.deepcopy(self.ar_dict)
        del test_dict['project']
        self.assertDictContainsSubset(test_dict,ar._loaded_values)

    def test_update_allocation_request(self):
        ar = AllocationRequest.objects.get(project=self.proj)
        self.assertEquals(ar.status,'w')
        ar.status = 'w'
        ar.save()
        self.assertEquals(ar.status,'w')
        self.assertIsNone(ar.approved_on)

    def test_approve_allocation_request(self):
        ar = AllocationRequest.objects.get(project=self.proj)
        self.assertEquals(ar.status,'w')
        ar.status = 'a'
        ar.save()
        self.assertEquals(ar.status,'a')
        self.assertIsNotNone(ar.approved_on)
        self.assertIsNotNone(ar.allocation)
