import django_filters
import rest_framework

from accounts.models import AccountRequest


class AccountRequestFilter(rest_framework.filters.FilterSet):
    min_date = django_filters.DateTimeFilter(name="request_date", lookup_type='gte')
    max_date = django_filters.DateTimeFilter(name="request_date", lookup_type='lte')
    class Meta:
        model = AccountRequest
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'organization',
            'course_number',
            'sponsor_email',
            'resources_requested',
            'status',
            'approved_on',
            'request_date',
        ]
