from rest_framework import viewsets
from rest_framework import generics
from rest_framework import filters

from endpoints.serializers import AccountRequestSerializer
from endpoints.filters import AccountRequestFilter
from endpoints.serializers import ProjectSerializer
from endpoints.filters import ProjectFilter

from accounts.models import AccountRequest
from projects.models import Project


# class AccountRequestList(generics.ListAPIView):
class AccountRequestList(viewsets.ReadOnlyModelViewSet):
    queryset = AccountRequest.objects.all()
    serializer_class = AccountRequestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AccountRequestFilter

class ProjectList(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectFilter
