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

class BaseCase(TestCase):
    directory = dict([admin, groups, people, test_user])

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

class RcLdapUserTestCase(BaseCase):
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_read(self):
        u = RcLdapUser.objects.get(username='testuser')

        # self.assertEquals(u.group, 1000)
        self.assertEquals(u.home_directory, '/home/testuser')
        self.assertEquals(u.uid, 1000)
        self.assertEquals(u.username, 'testuser')
        self.assertEquals(u.modified_date, datetime.datetime(2015,11,06,03,43,24))

        self.assertRaises(RcLdapUser.DoesNotExist, RcLdapUser.objects.get,
                          username='does_not_exist')

    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_update(self):
        u = RcLdapUser.objects.get(username='testuser')
        u.first_name = 'Tested'
        u.save()
        self.assertEquals(u.first_name, 'Tested')

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
