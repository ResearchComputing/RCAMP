from rest_framework import serializers
from accounts.models import AccountRequest


class AccountRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
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