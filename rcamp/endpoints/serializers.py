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
            'status',
            'approved_on',
            'request_date',
            'notes',
        )
