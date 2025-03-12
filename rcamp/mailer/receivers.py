from django.dispatch import receiver
from mailer.signals import *
from mailer.models import MailNotifier


@receiver(account_request_received)
def notify_account_request_received(sender, account_request, **kwargs):
    notifiers = MailNotifier.objects.filter(event='account_request_received')
    for notifier in notifiers:
        ctx = {'account_request':account_request}
        msg = notifier.send(context=ctx)

@receiver(account_request_approved)
def notify_account_request_approved(sender, account_request, **kwargs):
    notifiers = MailNotifier.objects.filter(event='account_request_approved')
    for notifier in notifiers:
        ctx = {'account_request':account_request}
        msg = notifier.send(context=ctx)

@receiver(account_created_from_request)
def notify_account_created_from_request(sender, account, **kwargs):
    notifiers = MailNotifier.objects.filter(event='account_created_from_request')
    for notifier in notifiers:
        ctx = {'account':account}
        msg = notifier.send(context=ctx)

@receiver(project_created_by_user)
def notify_project_created_by_user(sender, project, **kwargs):
    notifiers = MailNotifier.objects.filter(event='project_created_by_user')
    for notifier in notifiers:
        ctx = {'project':project}
        msg = notifier.send(context=ctx)

@receiver(allocation_request_created_by_user)
def notify_allocation_request_created_by_user(sender, allocation_request, requester, **kwargs):
    notifiers = MailNotifier.objects.filter(event='allocation_request_created_by_user')
    for notifier in notifiers:
        ctx = {
            'allocation_request': allocation_request,
            'requester': requester
        }
        msg = notifier.send(context=ctx)

@receiver(allocation_created_from_request)
def notify_allocation_created_from_request(sender, allocation, **kwargs):
    notifiers = MailNotifier.objects.filter(event='allocation_created_from_request')
    for notifier in notifiers:
        ctx = {'allocation':allocation}
        msg = notifier.send(context=ctx)

@receiver(allocation_expiring)
def notify_allocation_expiring(sender, allocation, **kwargs):
    notifiers = MailNotifier.objects.filter(event='allocation_expiring')
    for notifier in notifiers:
        ctx = {'allocation':allocation}
        msg = notifier.send(context=ctx)

@receiver(allocation_expired)
def notify_allocation_expired(sender, allocation, **kwargs):
    notifiers = MailNotifier.objects.filter(event='allocation_expired')
    for notifier in notifiers:
        ctx = {'allocation':allocation}
        msg = notifier.send(context=ctx)
