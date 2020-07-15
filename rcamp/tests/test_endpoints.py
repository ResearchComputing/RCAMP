from django.test import TestCase
from django.test import override_settings
import pytz
import json
import datetime

from tests.utilities.utils import (
    get_auth_user_defaults,
    SafeTestCase
)

from accounts.models import (
    AccountRequest,
    User
)
from projects.models import Project
from projects.models import Allocation


ucb_auth_user_dict = get_auth_user_defaults()
csu_auth_user_dict = get_auth_user_defaults()
csu_auth_user_dict['username'] = 'testuser@colostate.edu'

# This test case covers the AccountRequest API endpoint
class AccountRequestEndpointTestCase(SafeTestCase):
    def setUp(self):
        super(AccountRequestEndpointTestCase,self).setUp()
        self.ucb_auth_user = User.objects.create_user(
            ucb_auth_user_dict['username'],
            ucb_auth_user_dict['email'],
            ucb_auth_user_dict['password']
        )
        self.csu_auth_user = User.objects.create_user(
            csu_auth_user_dict['username'],
            csu_auth_user_dict['email'],
            csu_auth_user_dict['password']
        )

        ar_dict = dict(
            username='testuser1',
            first_name='test',
            last_name='user',
            email='tu@tu.org',
            login_shell='/bin/bash',
            resources_requested='summit',
            organization='ucb',
            role='staff',
            status='p'
        )
        self.ar1 = AccountRequest.objects.create(**ar_dict)

        ar_dict.update(dict(
            username='testuser2',
            email='tu2@tu.org',
            role='faculty',
            approved_on=pytz.timezone('America/Denver').localize(datetime.datetime(2016,04,01)),
            status='a'
        ))
        self.ar2 = AccountRequest.objects.create(**ar_dict)

        del ar_dict['resources_requested']
        ar_dict.update(dict(
            username='testuser3',
            email='tu3@tu.org',
            status='a',
            notes='approved!',
            id_verified_by='admin',
            approved_on=pytz.timezone('America/Denver').localize(datetime.datetime(2016,05,01)),
        ))
        self.ar3 = AccountRequest.objects.create(**ar_dict)

        self.client.login(username=self.ucb_auth_user.username, password="password")

    def test_ar_list(self):
        res = self.client.get('/api/accountrequests/')
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'username': 'testuser1',
                'status': 'p',
                'first_name': 'test',
                'last_name': 'user',
                'resources_requested': 'summit',
                'organization': 'ucb',
                'email': 'tu@tu.org',
            },
            {
                'username': 'testuser2',
                'status': 'a',
                'first_name': 'test',
                'last_name': 'user',
                'resources_requested': 'summit',
                'organization': 'ucb',
                'email': 'tu2@tu.org',
                'approved_on': '2016-04-01T00:00:00Z'
            },
            {
                'username': 'testuser3',
                'status': 'a',
                'first_name': 'test',
                'last_name': 'user',
                'resources_requested': None,
                'notes': 'approved!',
                'organization': 'ucb',
                'email': 'tu3@tu.org',
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_ar_post(self):
        post_data = dict(
            username = 'newuser',
            status = 'p',
            first_name = 'test',
            last_name = 'user',
            resources_requested = 'summit',
            organization = 'ucb',
            email = 'newtu@tu.org',
        )
        res = self.client.post('/api/accountrequests/', data=post_data)
        self.assertEquals(res.status_code, 201)

    def test_ar_detail(self):
        res = self.client.get('/api/accountrequests/testuser1/')
        self.assertEquals(res.status_code, 200)
        res_content = json.loads(res.content)
        expected_content = {
            'username': 'testuser1',
            'status': 'p',
            'first_name': 'test',
            'last_name': 'user',
            'resources_requested': 'summit',
            'organization': 'ucb',
            'email': 'tu@tu.org',
        }
        self.assertDictContainsSubset(expected_content,res_content)

    def test_ar_filter_dates(self):
        res = self.client.get(
            '/api/accountrequests/?min_approve_date={}&max_approve_date={}'.format(
                '2016-03-31',
                '2016-04-01'
            )
        )
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'username': 'testuser2',
                'status': 'a',
                'first_name': 'test',
                'last_name': 'user',
                'resources_requested': 'summit',
                'organization': 'ucb',
                'email': 'tu2@tu.org',
                'approved_on': '2016-04-01T00:00:00Z'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_ar_search(self):
        res = self.client.get(
            '/api/accountrequests/?search={}'.format(
                'tu2@tu.org'
            )
        )
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'username': 'testuser2',
                'status': 'a',
                'first_name': 'test',
                'last_name': 'user',
                'resources_requested': 'summit',
                'organization': 'ucb',
                'email': 'tu2@tu.org',
                'approved_on': '2016-04-01T00:00:00Z'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

# The test case covers the projects API endpoint
class ProjectEndpointTestCase(SafeTestCase):
    def setUp(self):
        super(ProjectEndpointTestCase,self).setUp()
        self.ucb_auth_user = User.objects.create_user(
            ucb_auth_user_dict['username'],
            ucb_auth_user_dict['email'],
            ucb_auth_user_dict['password']
        )
        self.csu_auth_user = User.objects.create_user(
            csu_auth_user_dict['username'],
            csu_auth_user_dict['email'],
            csu_auth_user_dict['password']
        )

        proj_dict = dict(
            pi_emails=['pi@pi.org'],
            organization='ucb',
            title='Test Project',
            description='A description.',
            project_id='ucb1',
            qos_addenda='+=viz'
        )
        self.proj1 = Project.objects.create(**proj_dict)
        self.proj1.managers.add(self.ucb_auth_user)
        self.proj1.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        proj_dict.update(dict(
            pi_emails=['pi2@pi.org'],
            project_id='ucb2',
            parent_account='ucball'
        ))
        del proj_dict['qos_addenda']
        self.proj2 = Project.objects.create(**proj_dict)
        self.proj2.created_on = datetime.datetime(2016,04,01)
        self.proj2.save()
        self.proj2.managers.add(self.ucb_auth_user)
        self.proj2.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        proj_dict.update(dict(
            pi_emails=['pi3@pi.org'],
            project_id='ucb3',
            notes='These are notes.'
        ))
        self.proj3 = Project.objects.create(**proj_dict)
        self.proj3.managers.add(self.ucb_auth_user)
        self.proj3.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        self.client.login(username=self.ucb_auth_user.username, password="password")

    def test_proj_list(self):
        res = self.client.get('/api/projects/')
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'collaborators': ['testuser','testuser@colostate.edu'],
                'managers': ['testuser'],
                'description': 'A description.',
                'title': 'Test Project',
                'deactivated': False,
                'pi_emails': "['pi@pi.org']",
                'qos_addenda': '+=viz',
                'organization': 'ucb',
                'project_id': 'ucb1'
            },
            {
                'collaborators': ['testuser','testuser@colostate.edu'],
                'managers': ['testuser'],
                'description': 'A description.',
                'title': 'Test Project',
                'deactivated': False,
                'pi_emails': "['pi2@pi.org']",
                'created_on': '2016-04-01',
                'organization': 'ucb',
                'project_id': 'ucb2',
                'parent_account': 'ucball',
            },
            {
                'collaborators': ['testuser','testuser@colostate.edu'],
                'managers': ['testuser'],
                'description': 'A description.',
                'title': 'Test Project',
                'deactivated': False,
                'notes': 'These are notes.',
                'pi_emails': "['pi3@pi.org']",
                'organization': 'ucb',
                'project_id': 'ucb3'
            },
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_proj_post(self):
        proj_dict = dict(
            pi_emails='["pi@pi.org"]',
            organization='ucb',
            title='Test Project',
            description='A description.',
            project_id='ucb14',
            qos_addenda='+=viz'
        )
        res = self.client.post('/api/projects/', data=proj_dict)
        self.assertEquals(res.status_code, 201)

    def test_proj_detail(self):
        res = self.client.get('/api/projects/ucb1/')
        self.assertEquals(res.status_code, 200)
        res_content = json.loads(res.content)
        expected_content = {
            'collaborators': ['testuser','testuser@colostate.edu'],
            'managers': ['testuser'],
            'description': 'A description.',
            'title': 'Test Project',
            'deactivated': False,
            'pi_emails': "['pi@pi.org']",
            'qos_addenda': '+=viz',
            'organization': 'ucb',
            'project_id': 'ucb1'
        }
        self.assertDictContainsSubset(expected_content,res_content)

    def test_proj_filter_dates(self):
        res = self.client.get(
            '/api/projects/?min_date={}&max_date={}'.format(
                '2016-03-31',
                '2016-04-01'
            )
        )
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'collaborators': ['testuser','testuser@colostate.edu'],
                'managers': ['testuser'],
                'description': 'A description.',
                'title': 'Test Project',
                'deactivated': False,
                'pi_emails': "['pi2@pi.org']",
                'created_on': '2016-04-01',
                'organization': 'ucb',
                'project_id': 'ucb2'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_proj_search(self):
        res = self.client.get(
            '/api/projects/?search={}'.format(
                'pi2@pi.org'
            )
        )
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'collaborators': ['testuser','testuser@colostate.edu'],
                'managers': ['testuser'],
                'description': 'A description.',
                'title': 'Test Project',
                'deactivated': False,
                'pi_emails': "['pi2@pi.org']",
                'created_on': '2016-04-01',
                'organization': 'ucb',
                'project_id': 'ucb2'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

# The test case covers the allocations API endpoint
class AllocationEndpointTestCase(SafeTestCase):
    def setUp(self):
        super(AllocationEndpointTestCase,self).setUp()
        self.ucb_auth_user = User.objects.create_user(
            ucb_auth_user_dict['username'],
            ucb_auth_user_dict['email'],
            ucb_auth_user_dict['password']
        )
        self.csu_auth_user = User.objects.create_user(
            csu_auth_user_dict['username'],
            csu_auth_user_dict['email'],
            csu_auth_user_dict['password']
        )

        proj_dict = dict(
            pi_emails=['pi@pi.org'],
            organization='ucb',
            title='Test Project',
            description='A description.',
            project_id='ucb1',
            parent_account='ucball',
            qos_addenda='+=viz'
        )
        self.proj1 = Project.objects.create(**proj_dict)
        self.proj1.created_on = datetime.datetime(2016,06,01)
        self.proj1.save()
        self.proj1.managers.add(self.ucb_auth_user)
        self.proj1.collaborators.add(self.ucb_auth_user,self.csu_auth_user)
        del proj_dict['parent_account']
        proj_dict['project_id'] = 'ucb2'
        self.proj2 = Project.objects.create(**proj_dict)
        self.proj2.created_on = datetime.datetime(2016,06,01)
        self.proj2.save()
        self.proj2.managers.add(self.ucb_auth_user)
        self.proj2.collaborators.add(self.ucb_auth_user,self.csu_auth_user)

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,02,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)
        alloc_dict = dict(
            project=self.proj1,
            amount=50000,
            start_date=sdate_tz,
            end_date=edate_tz
        )
        self.alloc1 = Allocation.objects.create(**alloc_dict)
        self.alloc1.created_on = datetime.datetime(2016,06,01)
        self.alloc1.save()
        edate = datetime.datetime(2017,03,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)
        alloc_dict['end_date'] = edate_tz
        self.alloc2 = Allocation.objects.create(**alloc_dict)
        self.alloc2.created_on = datetime.datetime(2016,04,01)
        self.alloc2.save()
        alloc_dict['project'] = self.proj2
        self.alloc3 = Allocation.objects.create(**alloc_dict)
        self.alloc3.created_on = datetime.datetime(2016,06,01)
        self.alloc3.save()

        self.client.login(username=self.ucb_auth_user.username, password="password")

    def test_alloc_list(self):
        res = self.client.get('/api/allocations/')
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'end_date': '2017-02-02',
                'allocation_id': 'ucb1_summit1',
                'created_on': '2016-06-01',
                'project': {
                    'collaborators': ['testuser','testuser@colostate.edu'],
                    'managers': ['testuser'],
                    'description': 'A description.',
                    'title': 'Test Project',
                    'deactivated': False,
                    'notes': None,
                    'pi_emails': "['pi@pi.org']",
                    'created_on': '2016-06-01',
                    'qos_addenda': '+=viz',
                    'organization': 'ucb',
                    'project_id': 'ucb1',
                    'parent_account': 'ucball'
                },
                'amount': 50000,
                'start_date': '2016-02-02'
            },
            {
                'end_date': '2017-03-02',
                'allocation_id': 'ucb1_summit2',
                'created_on': '2016-04-01',
                'project': {
                    'collaborators': ['testuser','testuser@colostate.edu'],
                    'managers': ['testuser'],
                    'description': 'A description.',
                    'title': 'Test Project',
                    'deactivated': False,
                    'notes': None,
                    'pi_emails': "['pi@pi.org']",
                    'created_on': '2016-06-01',
                    'qos_addenda': '+=viz',
                    'organization': 'ucb',
                    'project_id': 'ucb1',
                    'parent_account': 'ucball'
                },
                'amount': 50000,
                'start_date': '2016-02-02'
            },
            {
                'end_date': '2017-03-02',
                'allocation_id': 'ucb2_summit1',
                'created_on': '2016-06-01',
                'project': {
                    'collaborators': ['testuser','testuser@colostate.edu'],
                    'managers': ['testuser'],
                    'description': 'A description.',
                    'title': 'Test Project',
                    'deactivated': False,
                    'notes': None,
                    'pi_emails': "['pi@pi.org']",
                    'created_on': '2016-06-01',
                    'qos_addenda': '+=viz',
                    'organization': 'ucb',
                    'project_id': 'ucb2',
                    'parent_account': None
                },
                'amount': 50000,
                'start_date': '2016-02-02'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_alloc_post(self):
        res = self.client.post('/api/allocations/')
        self.assertEquals(res.status_code, 405)

    def test_alloc_detail(self):
        res = self.client.get('/api/allocations/ucb1_summit1/')
        self.assertEquals(res.status_code, 200)
        res_content = json.loads(res.content)
        expected_content = {
            'end_date': '2017-02-02',
            'allocation_id': 'ucb1_summit1',
            'created_on': '2016-06-01',
            'project': {
                'collaborators': ['testuser','testuser@colostate.edu'],
                'managers': ['testuser'],
                'description': 'A description.',
                'title': 'Test Project',
                'deactivated': False,
                'notes': None,
                'pi_emails': "['pi@pi.org']",
                'created_on': '2016-06-01',
                'qos_addenda': '+=viz',
                'organization': 'ucb',
                'project_id': 'ucb1',
                'parent_account': 'ucball'
            },
            'amount': 50000,
            'start_date': '2016-02-02'
        }
        self.assertDictContainsSubset(expected_content,res_content)

    def test_alloc_filter_dates(self):
        res = self.client.get(
            '/api/allocations/?min_date={}&max_date={}'.format(
                '2016-05-31',
                '2016-06-01'
            )
        )
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'end_date': '2017-02-02',
                'allocation_id': 'ucb1_summit1',
                'created_on': '2016-06-01',
                'project': {
                    'collaborators': ['testuser','testuser@colostate.edu'],
                    'managers': ['testuser'],
                    'description': 'A description.',
                    'title': 'Test Project',
                    'deactivated': False,
                    'notes': None,
                    'pi_emails': "['pi@pi.org']",
                    'created_on': '2016-06-01',
                    'qos_addenda': '+=viz',
                    'organization': 'ucb',
                    'project_id': 'ucb1',
                    'parent_account': 'ucball'
                },
                'amount': 50000,
                'start_date': '2016-02-02'
            },
            {
                'end_date': '2017-03-02',
                'allocation_id': 'ucb2_summit1',
                'created_on': '2016-06-01',
                'project': {
                    'collaborators': ['testuser','testuser@colostate.edu'],
                    'managers': ['testuser'],
                    'description': 'A description.',
                    'title': 'Test Project',
                    'deactivated': False,
                    'notes': None,
                    'pi_emails': "['pi@pi.org']",
                    'created_on': '2016-06-01',
                    'qos_addenda': '+=viz',
                    'organization': 'ucb',
                    'project_id': 'ucb2',
                    'parent_account': None
                },
                'amount': 50000,
                'start_date': '2016-02-02'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_alloc_search(self):
        res = self.client.get(
            '/api/allocations/?search={}'.format(
                'ucb2'
            )
        )
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                'end_date': '2017-03-02',
                'allocation_id': 'ucb2_summit1',
                'created_on': '2016-06-01',
                'project': {
                    'collaborators': ['testuser','testuser@colostate.edu'],
                    'managers': ['testuser'],
                    'description': 'A description.',
                    'title': 'Test Project',
                    'deactivated': False,
                    'notes': None,
                    'pi_emails': "['pi@pi.org']",
                    'created_on': '2016-06-01',
                    'qos_addenda': '+=viz',
                    'organization': 'ucb',
                    'project_id': 'ucb2',
                    'parent_account': None
                },
                'amount': 50000,
                'start_date': '2016-02-02'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])
