from mock import MagicMock
import mock
from django.test import override_settings

from lib.test.utils import SafeTestCase
from lib.test.ldap import build_mock_rcldap_user
from accounts.models import (
    User,
    AccountRequest,
    Intent
)
from projects.models import Project
from projects.receivers import update_general_account_membership


organization_info = {
    'ucb': {
        'long_name': 'University of Colorado Boulder',
        'suffix': None,
        'general_project_id': 'ucb-general'
    },
    'csu': {
        'long_name': 'Colorado State University',
        'suffix': 'colostate.edu',
        'general_project_id': 'csu-general'
    }
}

@override_settings(ORGANIZATION_INFO=organization_info)
class GeneralMembershipReceiverTestCase(SafeTestCase):
    def test_receiver_update_membership(self):
        ldap_user = build_mock_rcldap_user()
        ldap_user.organization = 'ucb'
        ldap_user.effective_uid = ldap_user.username

        auth_user_defaults = dict(
            username=ldap_user.username,
            first_name=ldap_user.first_name,
            last_name=ldap_user.last_name,
            email=ldap_user.email
        )
        auth_user = User.objects.create(**auth_user_defaults)

        account_request_defaults = dict(
            username=ldap_user.username,
            first_name=ldap_user.first_name,
            last_name=ldap_user.last_name,
            email=ldap_user.email,
            organization=ldap_user.organization
        )
        account_request = AccountRequest.objects.create(**account_request_defaults)
        intent = Intent.objects.create(
            account_request=account_request,
            reason_summit=True
        )

        project_defaults = dict(
            pi_emails=['pi@email.org'],
            description='test project',
            organization='ucb',
            title='test project',
            project_id='ucb-general'
        )
        project = Project.objects.create(**project_defaults)

        update_general_account_membership(ldap_user.__class__,account=ldap_user)

        project = Project.objects.get()
        self.assertIn(auth_user,project.collaborators.all())

        # No Summit intention declared
        project.collaborators.clear()
        intent.reason_summit = False
        intent.save()

        update_general_account_membership(ldap_user.__class__,account=ldap_user)

        project = Project.objects.get()
        self.assertNotIn(auth_user,project.collaborators.all())

    def test_receiver_update_membership_suffixed(self):
        ldap_user = build_mock_rcldap_user()
        ldap_user.organization = 'csu'
        ldap_user.effective_uid = '{}@colostate.edu'.format(ldap_user.username)

        auth_user_defaults = dict(
            username=ldap_user.effective_uid,
            first_name=ldap_user.first_name,
            last_name=ldap_user.last_name,
            email=ldap_user.email
        )
        auth_user = User.objects.create(**auth_user_defaults)

        account_request_defaults = dict(
            username=ldap_user.username,
            first_name=ldap_user.first_name,
            last_name=ldap_user.last_name,
            email=ldap_user.email,
            organization=ldap_user.organization
        )
        account_request = AccountRequest.objects.create(**account_request_defaults)
        intent = Intent.objects.create(
            account_request=account_request,
            reason_summit=True
        )

        project_defaults = dict(
            pi_emails=['pi@email.org'],
            description='test project',
            organization='csu',
            title='test project',
            project_id='csu-general'
        )
        project = Project.objects.create(**project_defaults)

        update_general_account_membership(ldap_user.__class__,account=ldap_user)

        project = Project.objects.get()
        self.assertIn(auth_user,project.collaborators.all())
