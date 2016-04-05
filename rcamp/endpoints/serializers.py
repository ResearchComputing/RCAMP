from rest_framework import serializers
from accounts.models import AccountRequest
from projects.models import Project


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
            'projects',
            'resources_requested',
            'status',
            'approved_on',
            'request_date',
            'notes',
        )

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
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
            'qos_addenda',
            'deactivated',
        )
