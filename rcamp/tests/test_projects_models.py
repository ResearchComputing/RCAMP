from mock import MagicMock
import mock
import copy
import datetime
import pytz

from django.conf import settings
from tests.utilities.utils import (
    SafeTestCase,
    get_auth_user_defaults
)

from accounts.models import User
from projects.models import (
    Project,
    Allocation,
    AllocationRequest
)


class ProjectTestCase(SafeTestCase):
    def setUp(self):
        self.proj_dict = {
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
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

class AllocationTestCase(SafeTestCase):

    def test_create_alloc_no_id(self):
        proj_dict = {
            'project_id': 'ucb7',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'organization':'ucb',
        }
        proj = Project.objects.create(**proj_dict)

        sdate = datetime.datetime(2016,2,2)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,2,2)
        edate_tz = pytz.timezone('America/Denver').localize(edate)

        alloc_dict = {
            'project': proj,
            'allocation_id': 'ucb7_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
        }
        alloc1 = Allocation.objects.create(**alloc_dict)

        alloc_dict = copy.deepcopy(alloc_dict)
        del alloc_dict['allocation_id']
        alloc = Allocation.objects.create(**alloc_dict)

        self.assertEqual(alloc.allocation_id,'ucb7_summit3')

    def test_create_alloc_no_id_multidigit_collision(self):
        proj_dict = {
            'project_id': 'ucb7',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'organization':'ucb',
        }
        proj = Project.objects.create(**proj_dict)
        proj2_dict = copy.deepcopy(proj_dict)
        proj2_dict['project_id'] = 'ucb78'
        proj2 = Project.objects.create(**proj2_dict)

        sdate = datetime.datetime(2016,2,2)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,2,2)
        edate_tz = pytz.timezone('America/Denver').localize(edate)

        alloc_dict = {
            'project': proj,
            'allocation_id': 'ucb78_summit1',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
        }
        alloc1 = Allocation.objects.create(**alloc_dict)

        alloc_dict = copy.deepcopy(alloc_dict)
        del alloc_dict['allocation_id']
        alloc = Allocation.objects.create(**alloc_dict)

        self.assertEqual(alloc.allocation_id,'ucb7_summit1')

class AllocationCreateTestCase(SafeTestCase):
    def setUp(self):
        super(AllocationCreateTestCase,self).setUp()
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'organization':'ucb',
        })
        self.ar_dict = {
            'project': self.proj,
            'amount_awarded': 1234
        }

    def test_create_allocation_from_request(self):
        alloc = Allocation.objects.create_allocation_from_request(**self.ar_dict)

        self.assertEqual(alloc.project,self.proj)
        self.assertEqual(alloc.amount,self.ar_dict['amount_awarded'])
        self.assertIsNotNone(alloc.start_date)
        self.assertIsNotNone(alloc.end_date)

    def test_create_allocation_from_request_increments_id(self):
        # Increment allocation to 4
        Allocation.objects.create_allocation_from_request(**self.ar_dict)
        Allocation.objects.create_allocation_from_request(**self.ar_dict)
        Allocation.objects.create_allocation_from_request(**self.ar_dict)
        alloc = Allocation.objects.create_allocation_from_request(**self.ar_dict)

        self.assertEqual(alloc.project,self.proj)
        self.assertEqual(alloc.amount,self.ar_dict['amount_awarded'])
        self.assertIsNotNone(alloc.start_date)
        self.assertIsNotNone(alloc.end_date)
        self.assertEqual(alloc.allocation_id, 'ucb1_summit4')

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
        self.assertRaises(
                TypeError,
                Allocation.objects.create_allocation_from_request,
                **tmp_dict
            )

# This test case covers AllocationRequest model functionality.
class AllocationRequestTestCase(SafeTestCase):
    def setUp(self):
        super(AllocationRequestTestCase,self).setUp()
        ucb_auth_user_defaults = get_auth_user_defaults()
        self.ucb_auth_user = User.objects.create_user(
            ucb_auth_user_defaults['username'],
            ucb_auth_user_defaults['email'],
            ucb_auth_user_defaults['password']
        )
        self.proj = Project.objects.create(**{
            'project_id': 'ucb1',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
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
            'requester': self.ucb_auth_user
        }
        ar = AllocationRequest.objects.create(**self.ar_dict)

    def test_update_allocation_request(self):
        ar = AllocationRequest.objects.get(project=self.proj)
        self.assertEqual(ar.status,'w')
        ar.status = 'w'
        ar.save()
        self.assertEqual(ar.status,'w')
        self.assertIsNone(ar.approved_on)

    def test_approve_allocation_request(self):
        ar = AllocationRequest.objects.get(project=self.proj)
        self.assertEqual(ar.status,'w')
        ar.status = 'a'
        ar.save()
        self.assertEqual(ar.status,'a')
        self.assertIsNotNone(ar.approved_on)
        self.assertIsNotNone(ar.allocation)
