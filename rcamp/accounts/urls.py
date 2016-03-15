from django.conf.urls import include, url
from accounts.views import ReasonView
from accounts.views import CuAccountRequestCreateView
from accounts.views import AccountRequestReviewView


urlpatterns = [
    url(
        r'^account-request/create$',
        ReasonView.as_view(),
        name='account-request-reason'
    ),
    url(
        r'^account-request/create/general$',
        CuAccountRequestCreateView.as_view(),
        name='account-request-create'
    ),
    url(
        r'^account-request/create/class$',
        CuAccountRequestCreateView.as_view(),
        name='class-account-request-create'
    ),
    url(
        r'^account-request/create/project$',
        CuAccountRequestCreateView.as_view(),
        name='project-account-request-create'
    ),
    url(
        r'^account-request/create/sponsored$',
        CuAccountRequestCreateView.as_view(),
        name='sponsored-account-request-create'
    ),
    url(
        r'^account-request/review/(?P<request_id>\d+)',
        AccountRequestReviewView.as_view(),
        name='account-request-review'
    ),
]
