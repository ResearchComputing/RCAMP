from rest_framework import viewsets
from rest_framework import generics
from rest_framework import filters

from endpoints.serializers import AccountRequestSerializer
from endpoints.filters import AccountRequestFilter

from accounts.models import AccountRequest


# class AccountRequestList(generics.ListAPIView):
class AccountRequestList(viewsets.ReadOnlyModelViewSet):
    queryset = AccountRequest.objects.all()
    serializer_class = AccountRequestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AccountRequestFilter
