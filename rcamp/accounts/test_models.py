from django.test import override_settings
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
        self.assertEquals(ldap_user.uid,1001)
        self.assertEquals(ldap_user.gid,1001)

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
        self.assertEquals(ldap_group.gid,1001)

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

def get_account_request_defaults():
    """Returns a dictionary of reasonable defaults for account request objects."""
    account_request_defaults = dict(
        username = 'testuser',
        first_name = 'Test',
        last_name = 'User',
        email = 'testuser@colorado.edu',
        role = 'faculty',
        department = 'physics',
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

        self.assertEquals(ldap_user.dn.lower(), 'uid=testuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(ldap_user.username, 'testuser')
        self.assertEquals(ldap_user.first_name, 'Test')
        self.assertEquals(ldap_user.last_name, 'User')
        self.assertEquals(ldap_user.full_name, 'User, Test')
        self.assertEquals(ldap_user.email, 'testuser@colorado.edu')
        self.assertEquals(ldap_user.uid, 9999)
        self.assertEquals(ldap_user.gid, 9999)
        self.assertEquals(ldap_user.gecos, 'Test User,,,')
        self.assertEquals(ldap_user.home_directory, '/home/testuser')
        self.assertEquals(ldap_user.login_shell, '/bin/bash')
        self.assertEquals(ldap_user.role, ['pi','faculty'])

        pgrp = RcLdapGroup.objects.get(name='testuserpgrp')
        sgrp = RcLdapGroup.objects.get(name='testusergrp')
        license_grp = RcLdapGroup.objects.get(name='ucb')

        self.assertEquals(pgrp.dn.lower(), 'cn=testuserpgrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(pgrp.gid, 9999)
        self.assertEquals(sgrp.dn.lower(), 'cn=testusergrp,ou=ucb,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(sgrp.gid, 1001)

        idt = IdTracker.objects.get(category='posix')
        self.assertEquals(idt.next_id,1002)

        self.assertEquals(pgrp.members, ['testuser'])
        self.assertEquals(sgrp.members, ['testuser'])
        self.assertEquals(license_grp.members, ['testuser'])

    def test_create_suffixed_user_from_request(self):
        dict_from_request = get_account_request_defaults()
        dict_from_request.update(dict(email='testuser@colostate.edu',organization='csu'))
        ldap_user = RcLdapUser.objects.create_user_from_request(**dict_from_request)

        self.assertEquals(ldap_user.dn.lower(), 'uid=testuser,ou=csu,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(ldap_user.uid, 1001)
        self.assertEquals(ldap_user.gid, 1001)
        self.assertEquals(ldap_user.home_directory, '/home/testuser@colostate.edu')

        pgrp = RcLdapGroup.objects.get(name='testuserpgrp')
        sgrp = RcLdapGroup.objects.get(name='testusergrp')

        self.assertEquals(pgrp.dn.lower(), 'cn=testuserpgrp,ou=csu,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(pgrp.gid, 1001)
        self.assertEquals(sgrp.dn.lower(), 'cn=testusergrp,ou=csu,ou=groups,dc=rc,dc=int,dc=colorado,dc=edu')
        self.assertEquals(sgrp.gid, 1002)
        self.assertEquals(pgrp.members, ['testuser'])
        self.assertEquals(sgrp.members, ['testuser'])

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

        self.assertEquals(ldap_user.dn.lower(), 'uid=testuser,ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu')
        today = datetime.date.today()
        expire = today.replace(year=today.year+1)
        expire_days = (expire - datetime.date(1970, 1, 1)).days
        self.assertEquals(ldap_user.expires, expire_days)

class AccountRequestTestCase(SafeTestCase):
    def setUp(self):
        super(AccountRequestTestCase,self).setUp()
        self.ar_dict = get_account_request_defaults()
        ar = AccountRequest.objects.create(**self.ar_dict)

    def test_update_account_request(self):
        ar = AccountRequest.objects.get(username='testuser')
        self.assertEquals(ar.status,'p')
        ar.save()
        self.assertEquals(ar.status,'p')
        self.assertIsNone(ar.approved_on)

    def test_approve_request(self):
        mock_ldap_manager = mock.MagicMock()
        mock_ldap_manager.create_user_from_request.return_value = None
        with mock.patch('accounts.models.RcLdapUser.objects',mock_ldap_manager):
            ar = AccountRequest.objects.get(username='testuser')
            ar.status = 'a'
            ar.save()
        expected_dict = copy.deepcopy(self.ar_dict)
        del expected_dict['department']
        mock_ldap_manager.create_user_from_request.assert_called_once_with(**expected_dict)
        self.assertIsNotNone(ar.approved_on)
        # Create new approved request
        new_req = get_account_request_defaults()
        new_req.update(dict(username='testuser1',email='testuser1@colorado.edu'))
        mock_ldap_manager.reset_mock()
        with mock.patch('accounts.models.RcLdapUser.objects',mock_ldap_manager):
            ar = AccountRequest.objects.create(status='a',**new_req)
        expected_dict = copy.deepcopy(new_req)
        del expected_dict['department']
        mock_ldap_manager.create_user_from_request.assert_called_once_with(**expected_dict)
        self.assertEquals(ar.status,'a')
        self.assertIsNotNone(ar.approved_on)
