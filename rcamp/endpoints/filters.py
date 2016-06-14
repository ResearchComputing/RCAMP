import django_filters
import rest_framework

from accounts.models import AccountRequest
from projects.models import Project
from projects.models import Allocation


class AccountRequestFilter(rest_framework.filters.FilterSet):
    min_request_date = django_filters.DateTimeFilter(name="request_date", lookup_type='gte')
    max_request_date = django_filters.DateTimeFilter(name="request_date", lookup_type='lte')
    min_approve_date = django_filters.DateTimeFilter(name="approved_on", lookup_type='gte')
    max_approve_date = django_filters.DateTimeFilter(name="approved_on", lookup_type='lte')
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
            'projects',
            'resources_requested',
            'status',
            'approved_on',
            'request_date',
        ]

class ProjectFilter(rest_framework.filters.FilterSet):
    min_date = django_filters.DateTimeFilter(name="created_on", lookup_type='gte')
    max_date = django_filters.DateTimeFilter(name="created_on", lookup_type='lte')
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
            'qos_addenda',
            'deactivated',
        ]

class AllocationFilter(rest_framework.filters.FilterSet):
    min_date = django_filters.DateTimeFilter(name="created_on", lookup_type='gte')
    max_date = django_filters.DateTimeFilter(name="created_on", lookup_type='lte')
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
