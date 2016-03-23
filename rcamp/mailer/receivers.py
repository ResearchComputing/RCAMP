from django.dispatch import receiver
from mailer.signals import *
from mailer.models import MailNotifier

@receiver(account_request_received)
def notify_account_request_received(sender, **kwargs):
    account_request = kwargs.get('account_request')

    notifiers = MailNotifier.objects.filter(event='account_request_received')
    for notifier in notifiers:
        ctx = {'account_request':account_request}
        msg = notifier.send(context=ctx)

@receiver(account_created_from_request)
def notify_account_created_from_request(sender, **kwargs):
    account = kwargs.get('account')

    notifiers = MailNotifier.objects.filter(event='account_created_from_request')
    for notifier in notifiers:
        ctx = {'account':account}
        msg = notifier.send(context=ctx)

@receiver(project_created_by_user)
def notify_project_created_by_user(sender, **kwargs):
    project = kwargs.get('project')

    notifiers = MailNotifier.objects.filter(event='project_created_by_user')
    for notifier in notifiers:
        ctx = {'project':project}
        msg = notifier.send(context=ctx)
