from django.test import override_settings
import mock
import datetime
import ldap
import copy

from django.conf import settings

from tests.utilities.utils import SafeTestCase
from tests.utilities.ldap import (
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
    RcLdapGroup,
    User
)


class RcLdapUserTestCase(LdapTestCase):
    def test_create_ldap_user(self):
        ldap_user_dict = get_ldap_user_defaults()
        with self.assertRaises(ValueError):
            RcLdapUser.objects.create(**ldap_user_dict)
        with self.assertRaises(ValueError):
            RcLdapUser.objects.create(organization='invalid_org',**ldap_user_dict)
        ldap_users = RcLdapUser.objects.all()
        self.assertEqual(ldap_users.count(),0)
        # Create ucb user
        RcLdapUser.objects.create(organization='ucb',**ldap_user_dict)
        ucb_user = RcLdapUser.objects.get(uid=1010)
        self.assertEqual(ucb_user.dn.lower(),'uid=testuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(ucb_user.organization,'ucb')
        self.assertEqual(ucb_user.effective_uid,'testuser')
        self.assertEqual(ucb_user.username,'testuser')
        # Create csu user
        csu_ldap_user_dict = get_ldap_user_defaults()
        csu_ldap_user_dict.update(dict(uid=1011,gid=1011))
        RcLdapUser.objects.create(organization='csu',**csu_ldap_user_dict)
        csu_user = RcLdapUser.objects.get(uid=1011)
        self.assertEqual(csu_user.dn.lower(),'uid=testuser,ou=csu,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(csu_user.organization,'csu')
        self.assertEqual(csu_user.effective_uid,'testuser@colostate.edu')
        self.assertEqual(csu_user.username,'testuser')

    def test_create_ldap_user_no_uid(self):
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )
        ldap_user_dict = get_ldap_user_defaults()
        del ldap_user_dict['uid']
        del ldap_user_dict['gid']
        RcLdapUser.objects.create(organization='ucb',**ldap_user_dict)
        ldap_user = RcLdapUser.objects.get(username='testuser')
        self.assertEqual(ldap_user.uid,1001)
        self.assertEqual(ldap_user.gid,1001)

    def test_get_ldap_user_from_suffixed_username(self):
        ucb_ldap_user_dict = get_ldap_user_defaults()
        csu_ldap_user_dict = get_ldap_user_defaults()
        csu_ldap_user_dict.update(dict(uid=1011,gid=1011))
        RcLdapUser.objects.create(organization='ucb',**ucb_ldap_user_dict)
        RcLdapUser.objects.create(organization='csu',**csu_ldap_user_dict)
        ucb_user = RcLdapUser.objects.get_user_from_suffixed_username('testuser')
        self.assertEqual(ucb_user.uid,1010)
        csu_user = RcLdapUser.objects.get_user_from_suffixed_username('testuser@colostate.edu')
        self.assertEqual(csu_user.uid,1011)

class RcLdapGroupTestCase(LdapTestCase):
    def test_create_ldap_group(self):
        ldap_group_dict = get_ldap_group_defaults()
        with self.assertRaises(ValueError):
            RcLdapGroup.objects.create(**ldap_group_dict)
        with self.assertRaises(ValueError):
            RcLdapGroup.objects.create(organization='invalid_org',**ldap_group_dict)
        ldap_groups = RcLdapGroup.objects.all()
        self.assertEqual(ldap_groups.count(),0)
        # Create ucb group
        RcLdapGroup.objects.create(organization='ucb',**ldap_group_dict)
        ucb_group = RcLdapGroup.objects.get(gid=1010)
        self.assertEqual(ucb_group.dn.lower(),'cn=testusergrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(ucb_group.organization,'ucb')
        self.assertEqual(ucb_group.effective_cn,'testusergrp')
        self.assertEqual(ucb_group.name,'testusergrp')
        # Create csu group
        csu_ldap_group_dict = get_ldap_group_defaults()
        csu_ldap_group_dict['gid'] = 1011
        RcLdapGroup.objects.create(organization='csu',**csu_ldap_group_dict)
        csu_group = RcLdapGroup.objects.get(gid=1011)
        self.assertEqual(csu_group.dn.lower(),'cn=testusergrp,ou=csu,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(csu_group.organization,'csu')
        self.assertEqual(csu_group.effective_cn,'testusergrp@colostate.edu')
        self.assertEqual(csu_group.name,'testusergrp')

    def test_create_ldap_group_no_gid(self):
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )
        ldap_group_dict = get_ldap_group_defaults()
        del ldap_group_dict['gid']
        RcLdapGroup.objects.create(organization='ucb',**ldap_group_dict)
        ldap_group = RcLdapGroup.objects.get(name='testusergrp')
        self.assertEqual(ldap_group.gid,1001)

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
        self.assertEqual(next_id, 1001)
        self.assertEqual(idt.next_id, 1002)

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
        self.assertEqual(next_id, 1001)
        self.assertEqual(idt.next_id, 1002)

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
        self.assertEqual(next_id, 1003)
        self.assertEqual(idt.next_id, 1004)

def get_account_request_defaults():
    """Returns a dictionary of reasonable defaults for account request objects."""
    account_request_defaults = dict(
        username = 'testuser',
        first_name = 'Test',
        last_name = 'User',
        email = 'testuser@colorado.edu',
        role = 'faculty',
        department = 'physics',
        discipline = 'Law',
        organization = 'ucb'
    )
    return account_request_defaults

class AccountCreationTestCase(LdapTestCase):
    def setUp(self):
        super(AccountCreationTestCase,self).setUp()
        idt = IdTracker.objects.create(
            category='posix',
            min_id=1000,
            max_id=1500,
            next_id=1001
        )
        # Create UCB license group
        license_grp_dict = dict(
            name = 'ucb',
            gid = 4000,
            members = []
        )
        RcLdapGroup.objects.create(organization='ucb',**license_grp_dict)

    @override_settings(LICENSE_GROUPS=dict(ucb = 'ucb'))
    def test_create_user_from_request(self):
        dict_from_request = get_account_request_defaults()
        mock_cu_user = mock.MagicMock(uid=9999)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            ldap_user = RcLdapUser.objects.create_user_from_request(**dict_from_request)

        self.assertEqual(ldap_user.dn.lower(), 'uid=testuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(ldap_user.username, 'testuser')
        self.assertEqual(ldap_user.first_name, 'Test')
        self.assertEqual(ldap_user.last_name, 'User')
        self.assertEqual(ldap_user.full_name, 'User, Test')
        self.assertEqual(ldap_user.email, 'testuser@colorado.edu')
        self.assertEqual(ldap_user.uid, 9999)
        self.assertEqual(ldap_user.gid, 9999)
        self.assertEqual(ldap_user.gecos, 'Test User,,,')
        self.assertEqual(ldap_user.home_directory, '/home/testuser')
        self.assertEqual(ldap_user.login_shell, '/bin/bash')
        self.assertEqual(ldap_user.role, ['pi','faculty'])

        pgrp = RcLdapGroup.objects.get(name='testuserpgrp')
        sgrp = RcLdapGroup.objects.get(name='testusergrp')
        license_grp = RcLdapGroup.objects.get(name='ucb')

        self.assertEqual(pgrp.dn.lower(), 'cn=testuserpgrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(pgrp.gid, 9999)
        self.assertEqual(sgrp.dn.lower(), 'cn=testusergrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(sgrp.gid, 1001)

        idt = IdTracker.objects.get(category='posix')
        self.assertEqual(idt.next_id,1002)

        self.assertEqual(pgrp.members, ['testuser'])
        self.assertEqual(sgrp.members, ['testuser'])
        self.assertEqual(license_grp.members, ['testuser'])

    def test_create_suffixed_user_from_request(self):
        dict_from_request = get_account_request_defaults()
        dict_from_request.update(dict(email='testuser@colostate.edu',organization='csu'))
        ldap_user = RcLdapUser.objects.create_user_from_request(**dict_from_request)

        self.assertEqual(ldap_user.dn.lower(), 'uid=testuser,ou=csu,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(ldap_user.uid, 1001)
        self.assertEqual(ldap_user.gid, 1001)
        self.assertEqual(ldap_user.home_directory, '/home/testuser@colostate.edu')

        pgrp = RcLdapGroup.objects.get(name='testuserpgrp')
        sgrp = RcLdapGroup.objects.get(name='testusergrp')

        self.assertEqual(pgrp.dn.lower(), 'cn=testuserpgrp,ou=csu,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(pgrp.gid, 1001)
        self.assertEqual(sgrp.dn.lower(), 'cn=testusergrp,ou=csu,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEqual(sgrp.gid, 1002)
        self.assertEqual(pgrp.members, ['testuser'])
        self.assertEqual(sgrp.members, ['testuser'])

    def test_create_user_from_request_missing_fields(self):
        user_dict = {
            'username': 'requestuser',
            'first_name': 'Request',
            'last_name': 'User',
            'email': 'requser@requests.org',
            'organization': 'ucb',
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

    def test_create_user_from_request_sponsored(self):
        dict_from_request = get_account_request_defaults()
        dict_from_request['role'] = 'sponsored'
        mock_cu_user = mock.MagicMock(uid=9999)
        with mock.patch('accounts.models.CuLdapUser.objects.get',return_value=mock_cu_user):
            ldap_user = RcLdapUser.objects.create_user_from_request(**dict_from_request)

        self.assertEqual(ldap_user.dn.lower(), 'uid=testuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        today = datetime.date.today()
        expire = today.replace(year=today.year+1)
        expire_days = (expire - datetime.date(1970, 1, 1)).days
        self.assertEqual(ldap_user.expires, expire_days)

class AccountRequestTestCase(SafeTestCase):
    def setUp(self):
        super(AccountRequestTestCase,self).setUp()
        self.ar_dict = get_account_request_defaults()
        ar = AccountRequest.objects.create(**self.ar_dict)

    def test_update_account_request(self):
        ar = AccountRequest.objects.get(username='testuser')
        self.assertEqual(ar.status,'p')
        ar.save()
        self.assertEqual(ar.status,'p')
        self.assertIsNone(ar.approved_on)

    def test_update_pending_account_request_approve_on_is_none(self):
        ar = AccountRequest.objects.get(username='testuser')
        ar.approved_on = datetime.date.today()
        self.assertEqual(ar.status,'p')
        self.assertIsNotNone(ar.approved_on)
        ar.save()
        self.assertEqual(ar.status,'p')
        self.assertIsNone(ar.approved_on)

    def test_approve_request(self):
        mock_ldap_manager = mock.MagicMock()
        mock_rc_ldap_user = build_mock_rcldap_user()
        mock_rc_ldap_user.organization = 'ucb'
        mock_rc_ldap_user.effective_uid = mock_rc_ldap_user.username
        mock_ldap_manager.create_user_from_request.return_value = mock_rc_ldap_user
        with mock.patch('accounts.models.RcLdapUser.objects',mock_ldap_manager),mock.patch('django.dispatch.Signal.send') as account_request_approved_mock:
            ar = AccountRequest.objects.get(username='testuser')
            ar.status = 'a'
            ar.save()
        expected_dict = copy.deepcopy(self.ar_dict)
        del expected_dict['department']
        mock_ldap_manager.create_user_from_request.assert_called_once_with(**expected_dict)
        self.assertIsNotNone(ar.approved_on)
        auth_user = User.objects.get(username=mock_rc_ldap_user.username)

        # Create new approved request
        new_req = get_account_request_defaults()
        new_req.update(dict(username='testuser1',email='testuser1@colorado.edu'))
        mock_ldap_manager.reset_mock()
        with mock.patch('accounts.models.RcLdapUser.objects',mock_ldap_manager),mock.patch('django.dispatch.Signal.send') as account_request_approved_mock:
            ar = AccountRequest.objects.create(status='a',**new_req)
        expected_dict = copy.deepcopy(new_req)
        del expected_dict['department']
        mock_ldap_manager.create_user_from_request.assert_called_once_with(**expected_dict)
        self.assertEqual(ar.status,'a')
        self.assertIsNotNone(ar.approved_on)
