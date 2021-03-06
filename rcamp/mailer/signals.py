import django.dispatch


account_request_received = django.dispatch.Signal(providing_args=['account_request'])
account_request_approved = django.dispatch.Signal(providing_args=['account_request'])
account_created_from_request = django.dispatch.Signal(providing_args=['account'])

project_created_by_user = django.dispatch.Signal(providing_args=['project'])

allocation_request_created_by_user = django.dispatch.Signal(providing_args=['allocation_request'])

allocation_created_from_request = django.dispatch.Signal(providing_args=['allocation'])

allocation_expiring = django.dispatch.Signal(providing_args=['allocation'])
allocation_expired = django.dispatch.Signal(providing_args=['allocation'])
