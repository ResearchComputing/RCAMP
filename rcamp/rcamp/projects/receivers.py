from django.dispatch import receiver
from django.conf import settings
from mailer.signals import account_request_approved
from lib.ldap_utils import get_suffixed_username

from accounts.models import (
    User,
    AccountRequest,
    Intent
)
from projects.models import Project


@receiver(account_request_approved)
def check_general_eligibility(sender, **kwargs):
    account_request = kwargs.get('account_request')
    organization = account_request.organization
    username = account_request.username

    try:
        if not account_request.intent.reason_summit:
            return
    except Intent.DoesNotExist:
        return

    effective_uid = get_suffixed_username(username,organization)
    auth_user = User.objects.get(username=effective_uid)
    general_project_id = settings.ORGANIZATION_INFO[organization].get('general_project_id',None)
    try:
        general_project = Project.objects.get(project_id=general_project_id)
        general_project.collaborators.add(auth_user)
    except Project.DoesNotExist:
        return
