from mock import MagicMock
import mock
from django.test import override_settings

from lib.test.utils import SafeTestCase
from lib.test.ldap import get_ldap_user_defaults
from accounts.models import (
    User,
    AccountRequest,
    Intent
)
from projects.models import Project
from projects.receivers import check_general_eligibility


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
class GeneralEligibilityReceiverTestCase(SafeTestCase):
    def test_check_general_eligibility(self):
        user_defaults = get_ldap_user_defaults()

        auth_user_defaults = dict(
            username=user_defaults['username'],
            first_name=user_defaults['first_name'],
            last_name=user_defaults['last_name'],
            email=user_defaults['email']
        )
        auth_user = User.objects.create(**auth_user_defaults)

        account_request_defaults = dict(
            username=auth_user.username,
            first_name=auth_user.first_name,
            last_name=auth_user.last_name,
            email=auth_user.email,
            organization='ucb'
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

        check_general_eligibility(account_request.__class__,account_request=account_request)

        project = Project.objects.get()
        self.assertIn(auth_user,project.collaborators.all())

        # No Summit intention declared
        project.collaborators.clear()
        intent.reason_summit = False
        intent.save()

        check_general_eligibility(account_request.__class__,account_request=account_request)

        project = Project.objects.get()
        self.assertNotIn(auth_user,project.collaborators.all())

    def test_check_general_eligibility_suffixed(self):
        user_defaults = get_ldap_user_defaults()
        effective_uid = '{}@colostate.edu'.format(user_defaults['username'])
        auth_user_defaults = dict(
            username=effective_uid,
            first_name=user_defaults['first_name'],
            last_name=user_defaults['last_name'],
            email=user_defaults['email']
        )
        auth_user = User.objects.create(**auth_user_defaults)

        account_request_defaults = dict(
            username=user_defaults['username'],
            first_name=auth_user.first_name,
            last_name=auth_user.last_name,
            email=auth_user.email,
            organization='csu'
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

        check_general_eligibility(account_request.__class__,account_request=account_request)

        project = Project.objects.get()
        self.assertIn(auth_user,project.collaborators.all())
