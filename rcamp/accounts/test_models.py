from django.test import TestCase
from django.test import override_settings
import datetime
import ldap

from django.conf import settings

from ldapdb.backends.ldap.compiler import query_as_ldap

from mockldap import MockLdap
# Create your tests here.


admin = ('cn=admin', {'userPassword': ['test']})
groups = ('ou=groups,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top', 'posixGroup'], 'ou': ['groups']})
people = ('ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
    'objectClass': ['top','person','inetorgperson','posixaccount'], 'ou': ['people']})
test_user = (
    'uid=test,ou=people,dc=rc,dc=int,dc=colorado,dc=edu', {
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

class UserTestCase(TestCase):
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

    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_get(self):
        from accounts.models import RcLdapUser
        from accounts.models import RcLdapGroup
        u = RcLdapUser.objects.get(username='testuser')

        # self.assertEquals(u.group, 1000)
        self.assertEquals(u.home_directory, '/home/testuser')
        self.assertEquals(u.uid, 1000)
        self.assertEquals(u.username, 'testuser')
        self.assertEquals(u.modified_date, datetime.datetime(2015,11,06,03,43,24))

        self.assertRaises(RcLdapUser.DoesNotExist, RcLdapUser.objects.get,
                          username='does_not_exist')

    # def test_update(self):
    #     u = RcLdapUser.objects.get(username='foouser')
    #     u.first_name = u'Foo2'
    #     u.save()

    #     # make sure DN gets updated if we change the pk
    #     u.username = 'foouser2'
    #     u.save()
    #     self.assertEquals(u.dn, 'uid=foouser2,%s' % RcLdapUser.base_dn)
        