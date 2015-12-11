import django.dispatch


account_request_received = django.dispatch.Signal(providing_args=['account_request'])
account_created_from_request = django.dispatch.Signal(providing_args=['account'])
