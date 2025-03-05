from django.conf.urls import include, url
from django.urls import path
from . import admin
from accounts.views import (
    AccountRequestOrgSelectView,
    AccountRequestVerifyUcbView,
    AccountRequestVerifyCsuView,
    AccountRequestIntentView,
    AccountRequestReviewView,
    sync_user_from_comanage
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
        AccountRequestVerifyCsuView.as_view(),
        name='account-request-verify-csu'
    ),
    url(
        r'^account-request/create/intent$',
        AccountRequestIntentView.as_view(),
        name='account-request-intent'
    ),
    url(
        r'^account-request/review$',
        AccountRequestReviewView.as_view(),
        name='account-request-review'
    ),
    path('admin/accounts/comanageuser/<int:user_id>/sync/', sync_user_from_comanage, name='accounts_comanageuser_sync'),
]
