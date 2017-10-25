from rest_framework import (
    viewsets,
    generics,
    filters,
    permissions
)
from endpoints.filters import (
    AccountRequestFilter,
    ProjectFilter,
    AllocationFilter
)
from endpoints.serializers import (
    AccountRequestSerializer,
    ProjectSerializer,
    AllocationSerializer
)

from accounts.models import AccountRequest
from projects.models import Project
from projects.models import Allocation


# class AccountRequestList(generics.ListAPIView):
class AccountRequestList(viewsets.ModelViewSet):
    queryset = AccountRequest.objects.all()
    serializer_class = AccountRequestSerializer
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    search_fields = ('username','first_name','last_name','email',)
    filter_class = AccountRequestFilter
    lookup_field = 'username'

class ProjectList(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter,)
    search_fields = ('project_id','pi_emails','managers','collaborators',)
    filter_class = ProjectFilter
    lookup_field = 'project_id'

class AllocationList(viewsets.ReadOnlyModelViewSet):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter,)
    search_fields = ('allocation_id','start_date','end_date','created_on',)
    filter_class = AllocationFilter
    lookup_field = 'allocation_id'
