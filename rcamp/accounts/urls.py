from django.conf.urls import include, url
from accounts.views import ReasonView
from accounts.views import AccountRequestCreateView
from accounts.views import SponsoredAccountRequestCreateView
from accounts.views import ClassAccountRequestCreateView
# from accounts.views import ProjectAccountRequestCreateView
from accounts.views import AccountRequestReviewView


urlpatterns = [
    url(
        r'^account-request/create$',
        ReasonView.as_view(),
        name='account-request-reason'
    ),
    url(
        r'^account-request/create/general$',
        AccountRequestCreateView.as_view(),
        name='account-request-create'
    ),
    url(
        r'^account-request/create/class$',
        ClassAccountRequestCreateView.as_view(),
        name='class-account-request-create'
    ),
    url(
        r'^account-request/create/sponsored$',
        SponsoredAccountRequestCreateView.as_view(),
        name='sponsored-account-request-create'
    ),
    url(
        r'^account-request/review/(?P<request_id>\d+)',
        AccountRequestReviewView.as_view(),
        name='account-request-review'
    ),
]
