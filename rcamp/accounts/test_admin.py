from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import ldap
import copy

from django.conf import settings
from ldapdb.backends.ldap.compiler import query_as_ldap

# Import namespace for mock
import accounts.models
from accounts.test_models import BaseCase
from accounts.models import IdTracker
from accounts.models import AccountRequest
from accounts.models import RcLdapUser
from accounts.models import RcLdapGroup

from mockldap import MockLdap
# Create your tests here.


admin = ('cn=admin', {'userPassword': ['test']})
groups = ('ou=groups,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top', 'posixGroup'], 'ou': ['groups']})
people = ('ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top','person','inetorgperson','posixaccount','curcPerson'], 'ou': ['people']})
cu_people = ('ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top','person','inetorgperson','posixaccount','curcPerson'], 'ou': ['people']})
xsede_people = ('ou=xsede,ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top','person','inetorgperson','posixaccount','curcPerson'], 'ou': ['people']})
test_user = (
    'uid=testuser,ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
        'objectClass': ['top', 'person', 'inetorgperson', 'posixaccount','curcPerson'],
        'cn': ['user, test'],
        'givenName': ['test'],
        'sn': ['user'],
        'mail': ['testuser@test.org'],
        'uid': ['testuser'],
        'modifytimestamp': ['20151106034324Z'],
        'uidNumber': ['1000'],
        'gidNumber': ['1000'],
        'gecos': [''],
        'homeDirectory': ['/home/testuser'],
        'loginShell': ['/bin/bash']
    }
)
test_cu_user = (
    'uid=testcuuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
        'objectClass': ['top', 'person', 'inetorgperson', 'posixaccount','curcPerson'],
        'cn': ['user, test'],
        'givenName': ['test'],
        'sn': ['user'],
        'mail': ['testuser@test.org'],
        'uid': ['testcuuser'],
        'modifytimestamp': ['20151106034324Z'],
        'uidNumber': ['1200'],
        'gidNumber': ['1200'],
        'gecos': [''],
        'homeDirectory': ['/home/cu/testuser'],
        'loginShell': ['/bin/bash'],
        'curcRole': ['pi','test'],
    }
)
test_group = (
    'cn=testgrp,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu', {
        'objectClass': ['top','posixGroup'],
        'cn': ['testgrp'],
        'gidNumber': ['1000'],
        'memberUid': ['testuser']
    }
)

class AdminTestCase(BaseCase):
    fixtures = ['test_users.json']
    
    def setUp(self):
        super(AdminTestCase,self).setUp()
        self.client.login(username="test_user", password="password")
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_index(self):
        response = self.client.get('/admin/accounts/')
        self.assertContains(response, "Account requests")
        self.assertContains(response, "Rc ldap groups")
        self.assertContains(response, "Rc ldap users")

class AdminRcLdapGroupTestCase(AdminTestCase):
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_group_list(self):
        response = self.client.get('/admin/accounts/rcldapgroup/')
        self.assertContains(response, "Rc ldap groups")
        self.assertContains(response, "testgrp")
        self.assertContains(response, "1000")
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_group_detail(self):
        response = self.client.get(
            '/admin/accounts/rcldapgroup/cn_3Dtestgrp_2Cou_3Dgroups_2Cdc_3Drc_2Cdc_3Dint_2Cdc_3Dcolorado_2Cdc_3Dedu/'
        )
        self.assertContains(response, "testgrp")
        self.assertContains(response, "1000")
        # Filter select field loaded:
        self.assertContains(response, "testuser")
        self.assertContains(response, "testcuuser")
    
    # @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    # def test_group_search(self):
    #     response = self.client.get('/admin/accounts/rcldapgroup/?q=test')
    #     self.assertContains(response, "Rc ldap groups")
    #     self.assertContains(response, "testgrp")
    #     self.assertContains(response, "1000")
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_group_add(self):
        response = self.client.post('/admin/accounts/rcldapgroup/add/',
                                    {'gid': '1002', 'name': 'creategrp'})
        self.assertRedirects(response, '/admin/accounts/rcldapgroup/')
        grp = RcLdapGroup.objects.get(name='creategrp')
        self.assertEquals(grp.dn, 'cn=creategrp,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_group_delete(self):
        response = self.client.post(
            '/admin/accounts/rcldapgroup/cn_3Dtestgrp_2Cou_3Dgroups_2Cdc_3Drc_2Cdc_3Dint_2Cdc_3Dcolorado_2Cdc_3Dedu/delete/',
            {'yes': 'post'}
        )
        self.assertRedirects(response, '/admin/accounts/rcldapgroup/')
        qs = RcLdapGroup.objects.filter(name='testgrp')
        self.assertEquals(qs.count(), 0)

class AdminRcLdapUserTestCase(AdminTestCase):
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_user_list(self):
        response = self.client.get('/admin/accounts/rcldapuser/')
        self.assertContains(response, "Rc ldap users")
        self.assertContains(response, "testuser")
        self.assertContains(response, "1000")
        self.assertContains(response, "testcuuser")
        self.assertContains(response, "1200")
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_user_detail(self):
        response = self.client.get(
            '/admin/accounts/rcldapuser/uid_3Dtestcuuser_2Cou_3Ducb_2Cou_3Dpeople_2Cdc_3Drc_2Cdc_3Dint_2Cdc_3Dcolorado_2Cdc_3Dedu/'
        )
        self.assertContains(response, "uid=testcuuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu")
        self.assertContains(response, "testcuuser")
        self.assertContains(response, "1200")
        self.assertContains(response, "University of Colorado Boulder")
    
    # @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    # def test_user_search(self):
    #     response = self.client.get('/admin/accounts/rcldapuser/?q=testcu')
    #     self.assertContains(response, "Rc ldap user")
    #     self.assertContains(response, "testcuuser")
    #     self.assertContains(response, "1200")
    #     self.assertNotContains(response, "testuser")
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_user_add(self):
        user_dict = dict(
            username='createuser',
            first_name='c',
            last_name='u',
            full_name='u, c',
            email='cu@cu.org',
            uid=1010,
            gid=1010,
            home_directory='/home/ucb/createuser',
            login_shell='/bin/bash',
            organization='ucb'
        )
        response = self.client.post('/admin/accounts/rcldapuser/add/',user_dict)
        self.assertRedirects(response, '/admin/accounts/rcldapuser/')
        u = RcLdapUser.objects.get(username='createuser')
        self.assertEquals(u.dn, 'uid=createuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
    
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_user_delete(self):
        response = self.client.post(
            '/admin/accounts/rcldapuser/uid_3Dtestcuuser_2Cou_3Ducb_2Cou_3Dpeople_2Cdc_3Drc_2Cdc_3Dint_2Cdc_3Dcolorado_2Cdc_3Dedu/delete/',
            {'yes': 'post'}
        )
        self.assertRedirects(response, '/admin/accounts/rcldapuser/')
        qs = RcLdapUser.objects.filter(username='testcuuser')
        self.assertEquals(qs.count(), 0)
