from django.conf.urls import include, url
from accounts.views import OrgSelectView
from accounts.views import CuAccountRequestCreateView
from accounts.views import AccountRequestReviewView


urlpatterns = [
    url(r'^account-request/create$', OrgSelectView.as_view(), name='account-request-org'),
    url(r'^account-request/create/ucb$', CuAccountRequestCreateView.as_view(), name='ucb-account-request-create'),
    url(r'^account-request/create/csu$', CuAccountRequestCreateView.as_view(), name='csu-account-request-create'),
    url(r'^account-request/create/xsede$', CuAccountRequestCreateView.as_view(), name='xsede-account-request-create'),
    url(r'^account-request/review/(?P<request_id>\d+)', AccountRequestReviewView.as_view(), name='account-request-review'),
]