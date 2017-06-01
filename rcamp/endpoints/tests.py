from django.test import TestCase
from django.test import override_settings
import pytz
import json
import datetime

from accounts.models import AccountRequest
from projects.models import Project
from projects.models import Allocation



# This test case covers the AccountRequest API endpoint
class AccountRequestEndpointTestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        super(AccountRequestEndpointTestCase,self).setUp()
        proj_dict = dict(
            pi_emails=['pi@pi.org'],
            managers=['pi@pi.prg','opi@pi.org'],
            collaborators=['tu@tu.org'],
            organization='ucb',
            title='Test Project',
            description='A description.',
            project_id='ucb1',
            qos_addenda='+=viz'
        )
        self.proj = Project.objects.create(**proj_dict)

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
        self.ar2.projects.add(self.proj)

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

        self.client.login(username="test_user", password="password")

    def test_ar_list(self):
        res = self.client.get('/api/accountrequests/')
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                u'username': u'testuser1',
                u'status': u'p',
                u'first_name': u'test',
                u'last_name': u'user',
                u'resources_requested': u'summit',
                u'organization': u'ucb',
                u'email': u'tu@tu.org',
            },
            {
                u'username': u'testuser2',
                u'status': u'a',
                u'first_name': u'test',
                u'last_name': u'user',
                u'resources_requested': u'summit',
                u'organization': u'ucb',
                u'email': u'tu2@tu.org',
                u'approved_on': u'2016-04-01T06:00:00Z',
                u'projects': [u'http://testserver/api/projects/ucb1/'],
            },
            {
                u'username': u'testuser3',
                u'status': u'a',
                u'first_name': u'test',
                u'last_name': u'user',
                u'resources_requested': None,
                u'notes': u'approved!',
                u'organization': u'ucb',
                u'email': u'tu3@tu.org',
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_ar_post(self):
        res = self.client.post('/api/accountrequests/')
        self.assertEquals(res.status_code, 405)

    def test_ar_detail(self):
        res = self.client.get('/api/accountrequests/testuser1/')
        self.assertEquals(res.status_code, 200)
        res_content = json.loads(res.content)
        expected_content = {
            u'username': u'testuser1',
            u'status': u'p',
            u'first_name': u'test',
            u'last_name': u'user',
            u'resources_requested': u'summit',
            u'organization': u'ucb',
            u'email': u'tu@tu.org',
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
                u'username': u'testuser2',
                u'status': u'a',
                u'first_name': u'test',
                u'last_name': u'user',
                u'resources_requested': u'summit',
                u'organization': u'ucb',
                u'email': u'tu2@tu.org',
                u'approved_on': u'2016-04-01T06:00:00Z',
                u'projects': [u'http://testserver/api/projects/ucb1/'],
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
                u'username': u'testuser2',
                u'status': u'a',
                u'first_name': u'test',
                u'last_name': u'user',
                u'resources_requested': u'summit',
                u'organization': u'ucb',
                u'email': u'tu2@tu.org',
                u'approved_on': u'2016-04-01T06:00:00Z',
                u'projects': [u'http://testserver/api/projects/ucb1/'],
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

# The test case covers the projects API endpoint
class ProjectEndpointTestCase(TestCase):
    def setUp(self):
        super(ProjectEndpointTestCase,self).setUp()
        proj_dict = dict(
            pi_emails=['pi@pi.org'],
            managers=['pi@pi.prg','opi@pi.org'],
            collaborators=['tu@tu.org'],
            organization='ucb',
            title='Test Project',
            description='A description.',
            project_id='ucb1',
            qos_addenda='+=viz'
        )
        self.proj1 = Project.objects.create(**proj_dict)

        proj_dict.update(dict(
            pi_emails=['pi2@pi.org'],
            project_id='ucb2',
            parent_account='ucball'
        ))
        del proj_dict['qos_addenda']
        self.proj2 = Project.objects.create(**proj_dict)
        self.proj2.created_on = datetime.datetime(2016,04,01)
        self.proj2.save()

        proj_dict.update(dict(
            pi_emails=['pi3@pi.org'],
            project_id='ucb3',
            notes='These are notes.'
        ))
        self.proj3 = Project.objects.create(**proj_dict)

    def test_proj_list(self):
        res = self.client.get('/api/projects/')
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                u'collaborators': u"[u'tu@tu.org']",
                u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                u'description': u'A description.',
                u'title': u'Test Project',
                u'deactivated': False,
                u'pi_emails': u"[u'pi@pi.org']",
                u'qos_addenda': u'+=viz',
                u'organization': u'ucb',
                u'project_id': u'ucb1'
            },
            {
                u'collaborators': u"[u'tu@tu.org']",
                u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                u'description': u'A description.',
                u'title': u'Test Project',
                u'deactivated': False,
                u'pi_emails': u"[u'pi2@pi.org']",
                u'created_on': u'2016-04-01',
                u'organization': u'ucb',
                u'project_id': u'ucb2',
                u'parent_account': u'ucball',
            },
            {
                u'collaborators': u"[u'tu@tu.org']",
                u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                u'description': u'A description.',
                u'title': u'Test Project',
                u'deactivated': False,
                u'notes': u'These are notes.',
                u'pi_emails': u"[u'pi3@pi.org']",
                u'organization': u'ucb',
                u'project_id': u'ucb3'
            },
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

    def test_proj_post(self):
        res = self.client.post('/api/projects/')
        self.assertEquals(res.status_code, 405)

    def test_proj_detail(self):
        res = self.client.get('/api/projects/ucb1/')
        self.assertEquals(res.status_code, 200)
        res_content = json.loads(res.content)
        expected_content = {
            u'collaborators': u"[u'tu@tu.org']",
            u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
            u'description': u'A description.',
            u'title': u'Test Project',
            u'deactivated': False,
            u'pi_emails': u"[u'pi@pi.org']",
            u'qos_addenda': u'+=viz',
            u'organization': u'ucb',
            u'project_id': u'ucb1'
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
                u'collaborators': u"[u'tu@tu.org']",
                u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                u'description': u'A description.',
                u'title': u'Test Project',
                u'deactivated': False,
                u'pi_emails': u"[u'pi2@pi.org']",
                u'created_on': u'2016-04-01',
                u'organization': u'ucb',
                u'project_id': u'ucb2'
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
                u'collaborators': u"[u'tu@tu.org']",
                u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                u'description': u'A description.',
                u'title': u'Test Project',
                u'deactivated': False,
                u'pi_emails': u"[u'pi2@pi.org']",
                u'created_on': u'2016-04-01',
                u'organization': u'ucb',
                u'project_id': u'ucb2'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])

# The test case covers the allocations API endpoint
class AllocationEndpointTestCase(TestCase):
    def setUp(self):
        super(AllocationEndpointTestCase,self).setUp()
        proj_dict = dict(
            pi_emails=['pi@pi.org'],
            managers=['pi@pi.prg','opi@pi.org'],
            collaborators=['tu@tu.org'],
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
        del proj_dict['parent_account']
        proj_dict['project_id'] = 'ucb2'
        self.proj2 = Project.objects.create(**proj_dict)
        self.proj2.created_on = datetime.datetime(2016,06,01)
        self.proj2.save()

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

    def test_alloc_list(self):
        res = self.client.get('/api/allocations/')
        self.assertEquals(res.status_code, 200)
        expected_content = [
            {
                u'end_date': u'2017-02-02',
                u'allocation_id': u'ucb1_summit1',
                u'created_on': u'2016-06-01',
                u'project': {
                    u'collaborators': u"[u'tu@tu.org']",
                    u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                    u'description': u'A description.',
                    u'title': u'Test Project',
                    u'deactivated': False,
                    u'notes': None,
                    u'pi_emails': u"[u'pi@pi.org']",
                    u'created_on': u'2016-06-01',
                    u'qos_addenda': u'+=viz',
                    u'organization': u'ucb',
                    u'project_id': u'ucb1',
                    u'parent_account': u'ucball'
                },
                u'amount': 50000,
                u'start_date': u'2016-02-02'
            },
            {
                u'end_date': u'2017-03-02',
                u'allocation_id': u'ucb1_summit2',
                u'created_on': u'2016-04-01',
                u'project': {
                    u'collaborators': u"[u'tu@tu.org']",
                    u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                    u'description': u'A description.',
                    u'title': u'Test Project',
                    u'deactivated': False,
                    u'notes': None,
                    u'pi_emails': u"[u'pi@pi.org']",
                    u'created_on': u'2016-06-01',
                    u'qos_addenda': u'+=viz',
                    u'organization': u'ucb',
                    u'project_id': u'ucb1',
                    u'parent_account': u'ucball'
                },
                u'amount': 50000,
                u'start_date': u'2016-02-02'
            },
            {
                u'end_date': u'2017-03-02',
                u'allocation_id': u'ucb2_summit1',
                u'created_on': u'2016-06-01',
                u'project': {
                    u'collaborators': u"[u'tu@tu.org']",
                    u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                    u'description': u'A description.',
                    u'title': u'Test Project',
                    u'deactivated': False,
                    u'notes': None,
                    u'pi_emails': u"[u'pi@pi.org']",
                    u'created_on': u'2016-06-01',
                    u'qos_addenda': u'+=viz',
                    u'organization': u'ucb',
                    u'project_id': u'ucb2',
                    u'parent_account': None
                },
                u'amount': 50000,
                u'start_date': u'2016-02-02'
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
            u'end_date': u'2017-02-02',
            u'allocation_id': u'ucb1_summit1',
            u'created_on': u'2016-06-01',
            u'project': {
                u'collaborators': u"[u'tu@tu.org']",
                u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                u'description': u'A description.',
                u'title': u'Test Project',
                u'deactivated': False,
                u'notes': None,
                u'pi_emails': u"[u'pi@pi.org']",
                u'created_on': u'2016-06-01',
                u'qos_addenda': u'+=viz',
                u'organization': u'ucb',
                u'project_id': u'ucb1',
                u'parent_account': u'ucball'
            },
            u'amount': 50000,
            u'start_date': u'2016-02-02'
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
                u'end_date': u'2017-02-02',
                u'allocation_id': u'ucb1_summit1',
                u'created_on': u'2016-06-01',
                u'project': {
                    u'collaborators': u"[u'tu@tu.org']",
                    u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                    u'description': u'A description.',
                    u'title': u'Test Project',
                    u'deactivated': False,
                    u'notes': None,
                    u'pi_emails': u"[u'pi@pi.org']",
                    u'created_on': u'2016-06-01',
                    u'qos_addenda': u'+=viz',
                    u'organization': u'ucb',
                    u'project_id': u'ucb1',
                    u'parent_account': u'ucball'
                },
                u'amount': 50000,
                u'start_date': u'2016-02-02'
            },
            {
                u'end_date': u'2017-03-02',
                u'allocation_id': u'ucb2_summit1',
                u'created_on': u'2016-06-01',
                u'project': {
                    u'collaborators': u"[u'tu@tu.org']",
                    u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                    u'description': u'A description.',
                    u'title': u'Test Project',
                    u'deactivated': False,
                    u'notes': None,
                    u'pi_emails': u"[u'pi@pi.org']",
                    u'created_on': u'2016-06-01',
                    u'qos_addenda': u'+=viz',
                    u'organization': u'ucb',
                    u'project_id': u'ucb2',
                    u'parent_account': None
                },
                u'amount': 50000,
                u'start_date': u'2016-02-02'
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
                u'end_date': u'2017-03-02',
                u'allocation_id': u'ucb2_summit1',
                u'created_on': u'2016-06-01',
                u'project': {
                    u'collaborators': u"[u'tu@tu.org']",
                    u'managers': u"[u'pi@pi.prg', u'opi@pi.org']",
                    u'description': u'A description.',
                    u'title': u'Test Project',
                    u'deactivated': False,
                    u'notes': None,
                    u'pi_emails': u"[u'pi@pi.org']",
                    u'created_on': u'2016-06-01',
                    u'qos_addenda': u'+=viz',
                    u'organization': u'ucb',
                    u'project_id': u'ucb2',
                    u'parent_account': None
                },
                u'amount': 50000,
                u'start_date': u'2016-02-02'
            }
        ]
        res_content = json.loads(res.content)
        for i in xrange(0,len(res_content)):
            self.assertDictContainsSubset(expected_content[i],res_content[i])
