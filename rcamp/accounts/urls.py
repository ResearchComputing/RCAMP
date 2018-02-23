from django.conf.urls import include, url
from accounts.views import (
    AccountRequestOrgSelectView,
    AccountRequestVerifyUcbView,
    AccountRequestIntentView,
    AccountRequestReviewView
)



urlpatterns = [
    url(
        r'^account-request/create/organization$',
        AccountRequestOrgSelectView.as_view(),
        name='account-request-org-select'
    ),
    url(
        r'^account-request/create/verify/ucb$',
        AccountRequestVerifyUcbView.as_view(),
        name='account-request-verify-ucb'
    ),
    url(
        r'^account-request/create/verify/csu$',
        AccountRequestVerifyUcbView.as_view(),
        name='account-request-verify-csu'
    ),
    url(
        r'^account-request/create/intent$',
        AccountRequestIntentView.as_view(),
        name='account-request-intent'
    ),
    url(
        r'^account-request/review/(?P<request_id>\d+)',
        AccountRequestReviewView.as_view(),
        name='account-request-review'
    ),
]
