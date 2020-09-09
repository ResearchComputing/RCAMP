import django_filters
import rest_framework

from accounts.models import AccountRequest
from projects.models import Project
from projects.models import Allocation


class AccountRequestFilter(django_filters.rest_framework.FilterSet):
    min_request_date = django_filters.DateTimeFilter(field_name="request_date", lookup_expr='gte')
    max_request_date = django_filters.DateTimeFilter(field_name="request_date", lookup_expr='lte')
    min_approve_date = django_filters.DateTimeFilter(field_name="approved_on", lookup_expr='gte')
    max_approve_date = django_filters.DateTimeFilter(field_name="approved_on", lookup_expr='lte')
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

class ProjectFilter(django_filters.rest_framework.FilterSet):
    min_date = django_filters.DateTimeFilter(field_name="created_on", lookup_expr='gte')
    max_date = django_filters.DateTimeFilter(field_name="created_on", lookup_expr='lte')
    class Meta:
        model = Project
        fields = [
            'pi_emails',
            'managers',
            'collaborators',
            'organization',
            'title',
            'description',
            'project_id',
            'created_on',
            'notes',
            'parent_account',
            'qos_addenda',
            'deactivated',
        ]

class AllocationFilter(django_filters.rest_framework.FilterSet):
    min_date = django_filters.DateTimeFilter(field_name="created_on", lookup_expr='gte')
    max_date = django_filters.DateTimeFilter(field_name="created_on", lookup_expr='lte')
    class Meta:
        model = Allocation
        fields = [
            'project',
            'allocation_id',
            'amount',
            'start_date',
            'end_date',
            'created_on',
        ]
