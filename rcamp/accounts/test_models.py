from django.test import TestCase
from django.test import override_settings
import datetime
import ldap

from django.conf import settings
from ldapdb.backends.ldap.compiler import query_as_ldap

from accounts.models import IdTracker
from accounts.models import RcLdapUser
from accounts.models import RcLdapGroup

from mockldap import MockLdap
# Create your tests here.


admin = ('cn=admin', {'userPassword': ['test']})
groups = ('ou=groups,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top', 'posixGroup'], 'ou': ['groups']})
people = ('ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top','person','inetorgperson','posixaccount'], 'ou': ['people']})
test_user = (
    'uid=testuser,ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
        'objectClass': ['top', 'person', 'inetorgperson', 'posixaccount'],
        'cn': ['test user'],
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
test_group = (
    'cn=testgrp,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu', {
        'objectClass': ['top','posixGroup'],
        'cn': ['testgrp'],
        'gidNumber': ['1000'],
        'memberUid': ['testuser']
    }
)

# Base class to set up mock LDAP server for the remainder
# of the test cases.
# 
# In each test that interacts with the mock LDAP, the
# DATABASE_ROUTERS setting will need to be overridden
# with the LDAP router for test.
class BaseCase(TestCase):
    directory = dict([admin, groups, people, test_user, test_group])

    @classmethod
    def setUpClass(cls):
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        self.mockldap.start()
        self.ldapobj = self.mockldap[settings.DATABASES['rcldap_test']['NAME']]

    def tearDown(self):
        self.mockldap.stop()
        del self.ldapobj

# Ensure basic functionality of the mock LDAP server
# before continuing onto the remainder of the test suite.
class MockLdapTestCase(BaseCase):
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_rcuser_read(self):
        u = RcLdapUser.objects.get(username='testuser')

        self.assertEquals(u.home_directory, '/home/testuser')
        self.assertEquals(u.uid, 1000)
        self.assertEquals(u.username, 'testuser')
        self.assertEquals(u.modified_date, datetime.datetime(2015,11,06,03,43,24))

        self.assertRaises(RcLdapUser.DoesNotExist, RcLdapUser.objects.get,
                        username='does_not_exist')

    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_rcuser_update(self):
        u = RcLdapUser.objects.get(username='testuser')
        u.first_name = 'Tested'
        u.save()
        self.assertEquals(u.first_name, 'Tested')
    
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_rcgroup_read(self):
        g = RcLdapGroup.objects.get(name='testgrp')
        
        self.assertEquals(g.name, 'testgrp')
        self.assertEquals(g.gid, 1000)
        self.assertEquals(g.members, ['testuser'])
        
        self.assertRaises(RcLdapGroup.DoesNotExist, RcLdapGroup.objects.get,
                        name='does_not_exist')
    
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_rcgroup_update(self):
        g = RcLdapGroup.objects.get(name='testgrp')
        g.name = 'testedgrp'
        g.save()
        self.assertEquals(g.name, 'testedgrp')

# This test case covers IdTracker functionality
class IdTrackerTestCase(BaseCase):
    def setUp(self):
        super(IdTrackerTestCase,self).setUp()
        idt = IdTracker(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )
        idt.save()
    
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_get_next_id(self):
        idt = IdTracker.objects.get(category='posix')
        self.assertEquals(idt.next_id, 1001)
        
        next_id = idt.get_next_id()
        self.assertEquals(next_id, 1001)
        self.assertEquals(idt.next_id, 1002)
    
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_get_next_id_no_initial_value(self):
        idt = IdTracker.objects.get(category='posix')
        idt.next_id = None
        idt.save()
        next_id = idt.get_next_id()
        self.assertEquals(next_id, 1001)
        self.assertEquals(idt.next_id, 1002)
    
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_get_next_id_conflict(self):
        idt = IdTracker.objects.get(category='posix')
        idt.next_id = 1000
        idt.save()
        next_id = idt.get_next_id()
        self.assertEquals(next_id, 1001)
        self.assertEquals(idt.next_id, 1002)

# This test case covers creating an LDAP user from
# a request dictionary.
class AccountCreationTestCase(BaseCase):
    def setUp(self):
        super(AccountCreationTestCase,self).setUp()
        idt = IdTracker(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )
        idt.save()
    
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_create_user_from_request(self):
        user_dict = {
            'username': 'requestuser',
            'first_name': 'Request',
            'last_name': 'User',
            'email': 'requser@requests.org',
            'organization': 'ucb'
        }
        u = RcLdapUser.objects.create_user_from_request(**user_dict)
        
        self.assertEquals(u.username, 'requestuser')
