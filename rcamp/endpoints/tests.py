from django.test import TestCase
from django.test import override_settings

from accounts.models import AccountRequest
from projects.models import Project



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
            resources_requested='janus,summit',
            organization='ucb',
            role='staff',
            status='p'
        )
        self.ar1 = AccountRequest.objects.create(**ar_dict)

        ar_dict.update(dict(
            username='testuser2',
            email='tu2@tu.org',
            role='faculty',
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
            id_verified_by='admin'
        ))
        self.ar3 = AccountRequest.objects.create(**ar_dict)

        self.client.login(username="test_user", password="password")

    def test_ar_list(self):
        res = self.client.get('/api/accountrequests/')
        self.assertContains(res,'tu@tu.org')
        self.assertContains(res,'tu2@tu.org')
        self.assertContains(res,'tu3@tu.org')
        self.assertContains(res,'/api/projects/1/')
