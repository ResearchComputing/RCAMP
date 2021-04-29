from django.conf import settings
import mock
import pam
from lib.pam_backend import PamBackend
from lib.ldap_backend import (
    AUTH_UCB_LDAP_Backend,
    AUTH_RC_LDAP_Backend,
    AUTH_CSU_LDAP_Backend
)
from tests.utilities.ldap import (
    LdapTestCase,
    get_ldap_user_defaults
)
from accounts.models import (
    RcLdapUser,
    User
)


# This test case covers functionality in the custom PAM Auth Backend
class PamBackendTestCase(LdapTestCase):
    def setUp(self):
        self.pb = PamBackend()
        super(PamBackendTestCase,self).setUp()

    @mock.patch('pam.pam.authenticate',mock.MagicMock(return_value=True))
    def test_authenticate(self):
        rc_user_defaults = get_ldap_user_defaults()
        RcLdapUser.objects.create(organization='ucb',**rc_user_defaults)
        rc_user = RcLdapUser.objects.get(username='testuser')
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(None, username='testuser',password='passwd')
        self.assertIsNotNone(user)
        self.assertEqual(user.username,rc_user.username)
        self.assertEqual(user.first_name,rc_user.first_name)
        self.assertEqual(user.last_name,rc_user.last_name)
        self.assertEqual(user.email,rc_user.email)

        reauthed_user = self.pb.authenticate(None, username='testuser',password='passwd')
        self.assertEqual(reauthed_user,user)
        self.assertFalse(reauthed_user.is_staff)

    @mock.patch('pam.pam.authenticate',mock.MagicMock(return_value=False))
    def test_authenticate_failed(self):
        rc_user_defaults = get_ldap_user_defaults()
        RcLdapUser.objects.create(organization='ucb',**rc_user_defaults)
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(None, username='testuser',password='badpasswd')
        self.assertIsNone(user)
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')

    @mock.patch('pam.pam.authenticate',mock.MagicMock(return_value=True))
    def test_authenticate_update_user(self):
        rc_user_defaults = get_ldap_user_defaults()
        RcLdapUser.objects.create(organization='ucb',**rc_user_defaults)
        rc_user = RcLdapUser.objects.get(username='testuser')
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(None, username='testuser',password='passwd')
        self.assertIsNotNone(user)

        rc_user.first_name = 'pamtested'
        rc_user.save(organization='ucb',)

        user = self.pb.authenticate(None, username='testuser',password='passwd')
        self.assertEqual(user.first_name,'pamtested')
        self.assertFalse(user.is_staff)

    @mock.patch('pam.pam.authenticate',mock.MagicMock(return_value=True))
    def test_get_user(self):
        rc_user_defaults = get_ldap_user_defaults()
        RcLdapUser.objects.create(organization='ucb',**rc_user_defaults)
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(None, username='testuser',password='passwd')
        self.assertIsNotNone(user)

        user = self.pb.get_user(user.id)
        self.assertEqual(user.username, 'testuser')


class AUTH_UCB_LDAPBackendTestCase(LdapTestCase):
    def setUp(self):
        self.ucb_ldap_backend = AUTH_UCB_LDAP_Backend()
        super(AUTH_UCB_LDAPBackendTestCase, self).setUp()

    def test_authenticate(self):
        rc_user_defaults = get_ldap_user_defaults()
        RcLdapUser.objects.create(organization='ucb',**rc_user_defaults)
        rc_user = RcLdapUser.objects.get(username='testuser')
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.ucb_ldap_backend.authenticate(None, username='testuser',password='passwd')
        self.assertIsNotNone(user)
        self.assertEqual(user.username,rc_user.username)
        self.assertEqual(user.first_name,rc_user.first_name)
        self.assertEqual(user.last_name,rc_user.last_name)
        self.assertEqual(user.email,rc_user.email)
