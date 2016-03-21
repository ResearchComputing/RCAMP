from django.contrib import admin
from django import forms
from lib.fields import LdapCsvField
from accounts.models import RcLdapUser
from accounts.models import CuLdapUser
from accounts.models import RcLdapGroup
from accounts.models import IdTracker
from accounts.models import AccountRequest
from accounts.models import ORGANIZATIONS


@admin.register(AccountRequest)
class AccountRequestAdmin(admin.ModelAdmin):
    def approve_requests(modeladmin, request, queryset):
        queryset.update(status='a')
    approve_requests.short_description = 'Approve selected account requests'
    actions = [approve_requests]
    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'organization',
        'request_date',
        'status'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'username',
        'role',
    ]

class RcLdapUserForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        instance = kwargs.get('instance')
        if instance:
            self.base_fields['organization'].initial = instance.org.split('=')[-1].lower()
            self.base_fields['dn'].widget.attrs['readonly'] = True
            self.base_fields['organization'].widget.attrs['disabled'] = True
        super(RcLdapUserForm,self).__init__(*args,**kwargs)
        try:
            self.initial['role'] = ','.join(self.instance.role)
        except TypeError:
            pass
        try:
            self.initial['affiliation'] = ','.join(self.instance.affiliation)
        except TypeError:
            pass
        self.fields['dn'].required = False
        self.fields['gecos'].required = False

    organization = forms.ChoiceField(required=False,choices=ORGANIZATIONS)
    role = LdapCsvField(required=False)
    affiliation = LdapCsvField(required=False)

    class Meta:
        model = RcLdapUser
        fields = [
            'dn',
            'organization',
            'username',
            'full_name',
            'first_name',
            'last_name',
            'email',
            'role',
            'affiliation',
            'uid',
            'gid',
            'gecos',
            'home_directory',
            'login_shell',
            'modified_date',
            'expires',
        ]

@admin.register(RcLdapUser)
class RcLdapUserAdmin(admin.ModelAdmin):
    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'uid',
        'organization',
        'role',
        'affiliation',
        'expires',
    ]
    search_fields = [
        'first_name',
        'last_name',
        'full_name',
        'username',
        # 'role',
        # 'affiliation',
    ]
    ordering = ('last_name',)
    form = RcLdapUserForm

    def save_model(self, request, obj, form, change):
        org = form.cleaned_data['organization'] or None
        obj.save(organization=org)

# Overrides default admin form for RcLdapGroups to allow
# for filtered multiselect widget.
class RcLdapGroupForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(RcLdapGroupForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))

        self.fields['gid'].required = False
        self.fields['members'].required = False
        self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Members',
                                        is_stacked=False)
    class Meta:
        model = RcLdapGroup
        fields = ['name','gid','members',]

@admin.register(RcLdapGroup)
class RcLdapGroupAdmin(admin.ModelAdmin):
    list_display = ['name','gid','members']
    search_fields = ['name']
    form = RcLdapGroupForm
