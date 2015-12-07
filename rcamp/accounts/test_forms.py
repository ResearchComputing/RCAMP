from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock
import datetime

from django.conf import settings

from accounts.forms import CuAuthForm
from accounts.models import CuLdapUser
from accounts.test_models import BaseCase


#Mock CU LDAP
admin = ('cn=admin', {'userPassword': ['test']})
people = ('ou=users,dc=colorado,dc=edu', {
    'objectClass': [], 'ou': ['users']})
test_user = (
    'uid=testuser,ou=users,dc=colorado,dc=edu', {
        'objectClass': [],
        'cn': ['user, test'],
        'givenName': ['test'],
        'sn': ['user'],
        'mail': ['testuser@test.org'],
        'uid': ['testuser'],
        'modifytimestamp': ['20151106034324Z'],
    }
)

# Base class to set up mock LDAP server for the remainder
# of the test cases.
# 
# In each test that interacts with the mock LDAP, the
# DATABASE_ROUTERS setting will need to be overridden
# with the LDAP router for test.
class CuBaseCase(BaseCase):
    directory = dict([admin, people, test_user])
    
    def setUp(self):
        self.mockldap.start()
        self.ldapobj = self.mockldap[settings.DATABASES['culdap_test']['NAME']]

# Cursory test to ensure mock LDAP is properly configured
class MockCuLdapTestCase(CuBaseCase):
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_cuuser_read(self):
        u = CuLdapUser.objects.get(username='testuser')
        
        self.assertEquals(u.username, 'testuser')
        self.assertEquals(u.modified_date, datetime.datetime(2015,11,06,03,43,24))
        
        self.assertRaises(CuLdapUser.DoesNotExist, CuLdapUser.objects.get,
                        username='does_not_exist')

# This test case covers the functionality of the CU auth form
# delivered to the user during account request. MagicMock is
# used as a stopgap while the custom LdapObject used for auth
# remains untestable.
class CuAuthFormTestCase(CuBaseCase):
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = CuAuthForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_form_invalid_bad_user(self):
        form_data = {
            'username': 'wronguser',
            'password': 'testpass',
        }
        form = CuAuthForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=False))
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_form_invalid_bad_password(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass',
        }
        form = CuAuthForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    @mock.patch('accounts.models.CuLdapUser.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['accounts.router.TestLdapRouter',])
    def test_form_invalid_missing_fields(self):
        form_data = {
            'username': 'testuser',
        }
        form = CuAuthForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        form_data = {
            'password': 'testpass',
        }
        form = CuAuthForm(data=form_data)
        self.assertFalse(form.is_valid())