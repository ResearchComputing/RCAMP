from django.dispatch import receiver
from django.conf import settings
from mailer.signals import *

from accounts.models import (
    User,
    AccountRequest
)
from projects.models import Project


@receiver(account_created_from_request)
def update_general_account_membership(sender, **kwargs):
    rc_ldap_user = kwargs.get('account')
    organization = rc_ldap_user.organization
    username = rc_ldap_user.username
    account_request = AccountRequest.objects.get(username=username,organization=organization)

    if not account_request.intent.reason_summit:
        return

    auth_user = User.objects.get(username=rc_ldap_user.effective_uid)
    general_project_id = settings.ORGANIZATION_INFO[organization].get('general_project_id',None)
    try:
        general_project = Project.objects.get(project_id=general_project_id)
        general_project.collaborators.add(auth_user)
    except Project.DoesNotExist:
        return
