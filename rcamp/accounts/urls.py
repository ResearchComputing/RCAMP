from django.conf.urls import include, url
from accounts.views import ReasonView
from accounts.views import AccountRequestCreateView
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
        AccountRequestCreateView.as_view(),
        name='class-account-request-create'
    ),
    url(
        r'^account-request/create/project$',
        AccountRequestCreateView.as_view(),
        name='project-account-request-create'
    ),
    url(
        r'^account-request/create/sponsored$',
        AccountRequestCreateView.as_view(),
        name='sponsored-account-request-create'
    ),
    url(
        r'^account-request/review/(?P<request_id>\d+)',
        AccountRequestReviewView.as_view(),
        name='account-request-review'
    ),
]
