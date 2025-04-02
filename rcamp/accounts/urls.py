from django.urls import include, path, re_path
from . import admin
from accounts.views import (
    AccountRequestOrgSelectView,
    AccountRequestVerifyUcbView,
    AccountRequestVerifyCsuView,
    AccountRequestIntentView,
    AccountRequestReviewView,
)


urlpatterns = [
    re_path(
        r'^account-request/create/organization$',
        AccountRequestOrgSelectView.as_view(),
        name='account-request-org-select'
    ),
    re_path(
        r'^account-request/create/verify/ucb$',
        AccountRequestVerifyUcbView.as_view(),
        name='account-request-verify-ucb'
    ),
    re_path(
        r'^account-request/create/verify/csu$',
        AccountRequestVerifyCsuView.as_view(),
        name='account-request-verify-csu'
    ),
    re_path(
        r'^account-request/create/intent$',
        AccountRequestIntentView.as_view(),
        name='account-request-intent'
    ),
    re_path(
        r'^account-request/review$',
        AccountRequestReviewView.as_view(),
        name='account-request-review'
    ),
]

# removed path('admin/accounts/comanageuser/<int:user_id>/sync/', sync_user_from_comanage, name='accounts_comanageuser_sync'),