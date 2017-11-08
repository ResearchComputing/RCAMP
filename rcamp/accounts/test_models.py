from django.test import override_settings
from mock import MagicMock
import mock
import datetime
import ldap
import copy

from django.conf import settings

from lib.test.utils import SafeTestCase
from lib.test.ldap import (
    get_ldap_user_defaults,
    get_ldap_group_defaults,
    build_mock_rcldap_user,
    build_mock_rcldap_group,
    LdapTestCase
)
# Import namespace for mock
import accounts.models
from accounts.models import (
    IdTracker,
    AccountRequest,
    RcLdapUser,
    RcLdapGroup
)


class RcLdapUserTestCase(LdapTestCase):
    def test_create_ldap_user(self):
        ldap_user_dict = get_ldap_user_defaults()
        with self.assertRaises(ValueError):
            RcLdapUser.objects.create(**ldap_user_dict)
        with self.assertRaises(ValueError):
            RcLdapUser.objects.create(organization='invalid_org',**ldap_user_dict)
        ldap_users = RcLdapUser.objects.all()
        self.assertEquals(ldap_users.count(),0)
        # Create ucb user
        RcLdapUser.objects.create(organization='ucb',**ldap_user_dict)
        ucb_user = RcLdapUser.objects.get(uid=1010)
        self.assertEquals(ucb_user.dn.lower(),'uid=testuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(ucb_user.organization,'ucb')
        self.assertEquals(ucb_user.effective_uid,'testuser')
        self.assertEquals(ucb_user.username,'testuser')
        # Create csu user
        csu_ldap_user_dict = get_ldap_user_defaults()
        csu_ldap_user_dict.update(dict(uid=1011,gid=1011))
        RcLdapUser.objects.create(organization='csu',**csu_ldap_user_dict)
        csu_user = RcLdapUser.objects.get(uid=1011)
        self.assertEquals(csu_user.dn.lower(),'uid=testuser,ou=csu,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(csu_user.organization,'csu')
        self.assertEquals(csu_user.effective_uid,'testuser@colostate.edu')
        self.assertEquals(csu_user.username,'testuser')

    def test_get_ldap_user_from_suffixed_username(self):
        ucb_ldap_user_dict = get_ldap_user_defaults()
        csu_ldap_user_dict = get_ldap_user_defaults()
        csu_ldap_user_dict.update(dict(uid=1011,gid=1011))
        RcLdapUser.objects.create(organization='ucb',**ucb_ldap_user_dict)
        RcLdapUser.objects.create(organization='csu',**csu_ldap_user_dict)
        ucb_user = RcLdapUser.objects.get_user_from_suffixed_username('testuser')
        self.assertEquals(ucb_user.uid,1010)
        csu_user = RcLdapUser.objects.get_user_from_suffixed_username('testuser@colostate.edu')
        self.assertEquals(csu_user.uid,1011)

class RcLdapGroupTestCase(LdapTestCase):
    def test_create_ldap_group(self):
        ldap_group_dict = get_ldap_group_defaults()
        with self.assertRaises(ValueError):
            RcLdapGroup.objects.create(**ldap_group_dict)
        with self.assertRaises(ValueError):
            RcLdapGroup.objects.create(organization='invalid_org',**ldap_group_dict)
        ldap_groups = RcLdapGroup.objects.all()
        self.assertEquals(ldap_groups.count(),0)
        # Create ucb group
        RcLdapGroup.objects.create(organization='ucb',**ldap_group_dict)
        ucb_group = RcLdapGroup.objects.get(gid=1010)
        self.assertEquals(ucb_group.dn.lower(),'cn=testusergrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(ucb_group.organization,'ucb')
        self.assertEquals(ucb_group.effective_cn,'testusergrp')
        self.assertEquals(ucb_group.name,'testusergrp')
        # Create csu group
        csu_ldap_group_dict = get_ldap_group_defaults()
        csu_ldap_group_dict['gid'] = 1011
        RcLdapGroup.objects.create(organization='csu',**csu_ldap_group_dict)
        csu_group = RcLdapGroup.objects.get(gid=1011)
        self.assertEquals(csu_group.dn.lower(),'cn=testusergrp,ou=csu,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(csu_group.organization,'csu')
        self.assertEquals(csu_group.effective_cn,'testusergrp@colostate.edu')
        self.assertEquals(csu_group.name,'testusergrp')

class IdTrackerTestCase(SafeTestCase):
    def test_get_next_id(self):
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )
        with mock.patch('accounts.models.RcLdapUser.objects.filter',return_value=[]):
            with mock.patch('accounts.models.RcLdapGroup.objects.filter',return_value=[]):
                next_id = idt.get_next_id()
        self.assertEquals(next_id, 1001)
        self.assertEquals(idt.next_id, 1002)

    def test_get_next_id_no_initial_value(self):
        mock_ldap_user = build_mock_rcldap_user(uid=1000)
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500
        )
        side_effects = [[mock_ldap_user], []]
        with mock.patch('accounts.models.RcLdapUser.objects.filter',side_effect=side_effects):
            with mock.patch('accounts.models.RcLdapGroup.objects.filter',return_value=[]):
                next_id = idt.get_next_id()
        self.assertEquals(next_id, 1001)
        self.assertEquals(idt.next_id, 1002)

    def test_get_next_id_conflict(self):
        mock_ldap_user = build_mock_rcldap_user(uid=1002)
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1002
        )
        side_effects = [[mock_ldap_user], []]
        with mock.patch('accounts.models.RcLdapUser.objects.filter',side_effect=side_effects):
            with mock.patch('accounts.models.RcLdapGroup.objects.filter',return_value=[]):
                next_id = idt.get_next_id()
        self.assertEquals(next_id, 1003)
        self.assertEquals(idt.next_id, 1004)

# This test case covers creating an LDAP user from
# a request dictionary.
class MockCuUser():
    uid = 999000

class AccountCreationTestCase(LdapTestCase):
    def setUp(self):
        super(AccountCreationTestCase,self).setUp()
        idt = IdTracker(
            category='posix',
            min_id=1000,
            max_id=1500
        )
        idt.save()

    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=MockCuUser)
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    @override_settings(LICENSE_GROUPS={'ucb':'ucb'})
    def test_create_user_from_request(self,mock_cu_user):
        user_dict = {
            'username': 'requestuser',
            'first_name': 'Request',
            'last_name': 'User',
            'email': 'requser@requests.org',
            'role': 'faculty',
            'organization': 'ucb',
            'login_shell': '/bin/bash',
        }
        u = RcLdapUser.objects.create_user_from_request(**user_dict)

        self.assertEquals(u.dn, 'uid=requestuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(u.username, 'requestuser')
        self.assertEquals(u.first_name, 'Request')
        self.assertEquals(u.last_name, 'User')
        self.assertEquals(u.full_name, 'User, Request')
        self.assertEquals(u.email, 'requser@requests.org')
        self.assertEquals(u.uid, 999000)
        self.assertEquals(u.gid, 999000)
        self.assertEquals(u.gecos, 'Request User,,,')
        self.assertEquals(u.home_directory, '/home/requestuser')
        self.assertEquals(u.login_shell, '/bin/bash')
        self.assertEquals(u.role, ['pi','faculty'])

        idt = IdTracker.objects.get(category='posix')
        self.assertEquals(idt.next_id, 1002)

        pgrp = RcLdapGroup.objects.get(name='requestuserpgrp')
        sgrp = RcLdapGroup.objects.get(name='requestusergrp')
        license_grp = RcLdapGroup.objects.get(name='ucb')

        self.assertEquals(pgrp.dn, 'cn=requestuserpgrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(pgrp.gid, 999000)
        self.assertEquals(sgrp.dn, 'cn=requestusergrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(sgrp.gid, 1001)
        for grp in [pgrp,sgrp]:
            self.assertEquals(grp.members, ['requestuser'])
        # self.assertEquals(license_grp.members,['requestuser'])

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_create_xsede_user_from_request(self):
        user_dict = {
            'username': 'requestuser',
            'first_name': 'Request',
            'last_name': 'User',
            'email': 'requser@requests.org',
            'role': 'faculty',
            'organization': 'xsede',
            'login_shell': '/bin/bash',
        }
        u = RcLdapUser.objects.create_user_from_request(**user_dict)

        self.assertEquals(u.dn, 'uid=requestuser,ou=xsede,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(u.username, 'requestuser')
        self.assertEquals(u.first_name, 'Request')
        self.assertEquals(u.last_name, 'User')
        self.assertEquals(u.full_name, 'User, Request')
        self.assertEquals(u.email, 'requser@requests.org')
        self.assertEquals(u.uid, 1001)
        self.assertEquals(u.gid, 1001)
        self.assertEquals(u.gecos, 'Request User,,,')
        self.assertEquals(u.home_directory, '/home/requestuser@xsede.org')
        self.assertEquals(u.login_shell, '/bin/bash')
        self.assertEquals(u.role, ['pi','faculty'])

        idt = IdTracker.objects.get(category='posix')
        self.assertEquals(idt.next_id, 1003)

        pgrp = RcLdapGroup.objects.get(name='requestuserpgrp')
        sgrp = RcLdapGroup.objects.get(name='requestusergrp')

        self.assertEquals(pgrp.dn, 'cn=requestuserpgrp,ou=xsede,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(pgrp.gid, 1001)
        self.assertEquals(sgrp.dn, 'cn=requestusergrp,ou=xsede,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(sgrp.gid, 1002)
        for grp in [pgrp,sgrp]:
            self.assertEquals(grp.members, ['requestuser'])

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_create_user_from_request_missing_fields(self):
        user_dict = {
            'username': 'requestuser',
            'first_name': 'Request',
            'last_name': 'User',
            'email': 'requser@requests.org',
            'organization': 'ucb',
            'login_shell': '/bin/bash',
        }

        for k in user_dict.keys():
            tmp_dict = copy.deepcopy(user_dict)
            del tmp_dict[k]
            self.assertRaises(
                    TypeError,
                    RcLdapUser.objects.create_user_from_request,
                    **tmp_dict
                )

        self.assertRaises(
                RcLdapGroup.DoesNotExist,
                RcLdapGroup.objects.get,
                gid=1001
            )

    @mock.patch('accounts.models.CuLdapUser.objects.get',return_value=MockCuUser)
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_create_user_from_request_sponsored(self,mock_cu_user):
        user_dict = {
            'username': 'requestuser',
            'first_name': 'Request',
            'last_name': 'User',
            'email': 'requser@requests.org',
            'role': 'sponsored',
            'organization': 'ucb',
            'login_shell': '/bin/bash',
        }
        u = RcLdapUser.objects.create_user_from_request(**user_dict)

        self.assertEquals(u.dn, 'uid=requestuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        today = datetime.date.today()
        expire = today.replace(year=today.year+1)
        expire_days = (expire - datetime.date(1970, 1, 1)).days
        self.assertEquals(u.expires, expire_days)

class MockLdapObjectManager():
    create_user_from_request = MagicMock(return_value={})

# This test case covers AccountRequest model functionality.
class AccountRequestTestCase(LdapTestCase):
    def setUp(self):
        super(AccountRequestTestCase,self).setUp()
        self.ar_dict = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'tu@tu.org',
            'role': 'faculty',
            'organization': 'ucb',
            'login_shell': '/bin/bash',
        }
        ar = AccountRequest.objects.create(**self.ar_dict)
        MockLdapObjectManager.create_user_from_request.reset_mock()

    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_update_account_request(self):
        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.status,'p')
        ar.status = 'p'
        ar.save()
        self.assertEquals(ar.status,'p')
        self.assertIsNone(ar.approved_on)

    @mock.patch('accounts.models.RcLdapUser.objects',MockLdapObjectManager)
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_update_approved_request(self):
        new_req = copy.deepcopy(self.ar_dict)
        new_req['username'] = 'testuser1'
        new_req['email'] = 'tu1@tu.org'
        new_req['status'] = 'a'
        ar = AccountRequest.objects.create(**new_req)
        ar.first_name = 'Bob'
        ar.save()
        self.assertEqual(MockLdapObjectManager.create_user_from_request.call_count, 1)

    @mock.patch('accounts.models.RcLdapUser.objects',MockLdapObjectManager)
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_create_and_approve_request(self):
        new_req = copy.deepcopy(self.ar_dict)
        new_req['username'] = 'testuser1'
        new_req['email'] = 'tu1@tu.org'
        new_req['status'] = 'a'
        ar = AccountRequest.objects.create(**new_req)
        self.assertEquals(ar.status,'a')
        self.assertIsNotNone(ar.approved_on)

    @mock.patch('accounts.models.RcLdapUser.objects',MockLdapObjectManager)
    @override_settings(DATABASE_ROUTERS=['lib.router.TestLdapRouter',])
    def test_approve_account_request(self):
        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.status,'p')
        ar.status = 'p'
        ar.save()
        ar.status = 'a'
        ar.save()
        self.assertEquals(ar.status,'a')
        self.assertIsNotNone(ar.approved_on)
        RcLdapUser.objects.create_user_from_request.assert_called_with(**self.ar_dict)
