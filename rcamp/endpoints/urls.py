from django.urls import include, re_path
from rest_framework import routers

from endpoints.viewsets import AccountRequestList
from endpoints.viewsets import ProjectList
from endpoints.viewsets import AllocationList

from accounts.models import AccountRequest
from projects.models import Project
from projects.models import Allocation


router = routers.DefaultRouter()
router.register(r'accountrequests', AccountRequestList)
router.register(r'projects', ProjectList)
router.register(r'allocations', AllocationList)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^auth/',include('rest_framework.urls', namespace='rest_framework')),
]
