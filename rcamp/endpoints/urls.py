from django.conf.urls import include, url
from rest_framework import routers

from endpoints.viewsets import AccountRequestList

from accounts.models import AccountRequest


router = routers.DefaultRouter()
router.register(r'accountrequests', AccountRequestList)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/',include('rest_framework.urls', namespace='rest_framework')),
]
