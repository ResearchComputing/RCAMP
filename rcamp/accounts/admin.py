from django.contrib import admin
from accounts.models import RcLdapUser
from accounts.models import CuLdapUser
from accounts.models import RcLdapGroup
from accounts.models import IdTracker
from accounts.models import AccountRequest


@admin.register(AccountRequest)
class AccountRequestAdmin(admin.ModelAdmin):
    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'organization',
        'request_date',
        'status'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'username'
    ]

# Register your models here.
admin.site.register(RcLdapUser)
admin.site.register(CuLdapUser)
admin.site.register(RcLdapGroup)
admin.site.register(IdTracker)
