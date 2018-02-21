from django.conf.urls import include, url
from accounts.views import (
    OrgSelectView,
    AccountRequestCreateUcbView,
    AccountRequestIntentView
)
# from accounts.views import AccountRequestCreateCsuView
# from accounts.views import AccountRequestReviewView


urlpatterns = [
    url(
        r'^account-request/create$',
        OrgSelectView.as_view(),
        name='account-request-org-select'
    ),
    url(
        r'^account-request/create/ucb$',
        AccountRequestCreateUcbView.as_view(),
        name='account-request-create-ucb'
    ),
    url(
        r'^account-request/create/csu$',
        AccountRequestCreateUcbView.as_view(),
        name='account-request-create-csu'
    ),
    url(
        r'^account-request/create/intent$',
        AccountRequestIntentView.as_view(),
        name='account-request-intent'
    ),
    # url(
    #     r'^account-request/review/(?P<request_id>\d+)',
    #     AccountRequestReviewView.as_view(),
    #     name='account-request-review'
    # ),
]
