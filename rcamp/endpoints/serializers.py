from rest_framework import serializers
from accounts.models import AccountRequest
from projects.models import Project
from projects.models import Allocation


class AccountRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'projects': {
                'lookup_field': 'project_id',
            }
        }
        lookup_field = 'username'
        model = AccountRequest
        fields = (
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
            'notes',
        )

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    managers = serializers.StringRelatedField(many=True)
    collaborators = serializers.StringRelatedField(many=True)

    class Meta:
        lookup_field = 'project_id'
        model = Project
        fields = (
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
        )

class AllocationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(many=False,read_only=True)
    class Meta:
        lookup_field = 'allocation_id'
        model = Allocation
        fields = (
            'project',
            'allocation_id',
            'amount',
            'start_date',
            'end_date',
            'created_on',
        )
