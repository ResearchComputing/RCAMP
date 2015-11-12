from django.conf.urls import include, url
from accounts.views import OrgSelectView

urlpatterns = [
    url(r'^account-request/create$', OrgSelectView.as_view(), name='account-request-org'),
    url(r'^account-request/create/(?P<org>\w+)$', OrgSelectView.as_view(), name='account-request-create'),
]