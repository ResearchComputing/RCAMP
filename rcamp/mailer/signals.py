import django.dispatch

account_request_received = django.dispatch.Signal()
account_request_approved = django.dispatch.Signal()
account_created_from_request = django.dispatch.Signal()

project_created_by_user = django.dispatch.Signal()

allocation_request_created_by_user = django.dispatch.Signal()

allocation_created_from_request = django.dispatch.Signal()

allocation_expiring = django.dispatch.Signal()
allocation_expired = django.dispatch.Signal()
