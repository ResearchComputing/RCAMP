from django.test import TestCase
from django.test import override_settings
from mock import MagicMock
import mock

from django.conf import settings
from django.contrib.auth.models import User

import pam
from lib.pam_backend import PamBackend

from accounts.models import RcLdapUser
from accounts.test_models import BaseCase

from mockldap import MockLdap



# This test case covers functionality in the custom PAM Auth Backend
class PamBackendTestCase(BaseCase):
    def setUp(self):
        self.pb = PamBackend()
        super(PamBackendTestCase,self).setUp()

    @mock.patch('pam.pam.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_authenticate(self):
        rc_user = RcLdapUser.objects.get(username='testuser')
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(username='testuser',password='passwd')
        self.assertIsNotNone(user)
        self.assertEqual(user.username,rc_user.username)
        self.assertEqual(user.first_name,rc_user.first_name)
        self.assertEqual(user.last_name,rc_user.last_name)
        self.assertEqual(user.email,rc_user.email)

        reauthed_user = self.pb.authenticate(username='testuser',password='passwd')
        self.assertEqual(reauthed_user,user)

    @mock.patch('pam.pam.authenticate',MagicMock(return_value=False))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_authenticate_failed(self):
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(username='testuser',password='badpasswd')
        self.assertIsNone(user)
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')

    @mock.patch('pam.pam.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_authenticate_update_user(self):
        rc_user = RcLdapUser.objects.get(username='testuser')
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(username='testuser',password='passwd')
        self.assertIsNotNone(user)

        rc_user.first_name = 'pamtested'
        rc_user.save()

        user = self.pb.authenticate(username='testuser',password='passwd')
        self.assertEqual(user.first_name,'pamtested')

    @mock.patch('pam.pam.authenticate',MagicMock(return_value=True))
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_get_user(self):
        self.assertRaises(User.DoesNotExist, User.objects.get,
                        username='testuser')
        user = self.pb.authenticate(username='testuser',password='passwd')
        self.assertIsNotNone(user)

        user = self.pb.get_user(user.id)
        self.assertEqual(user.username, 'testuser')
