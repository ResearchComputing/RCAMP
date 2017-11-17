from django.contrib import admin
from django import forms
from lib.fields import LdapCsvField
from accounts.models import (
    User,
    RcLdapUser,
    CuLdapUser,
    RcLdapGroup,
    IdTracker,
    AccountRequest,
    ORGANIZATIONS
)
# from projects.models import Project


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username','organization','first_name','last_name','email']
    search_fields = ['username','first_name','last_name','email']

class AccountRequestAdminForm(forms.ModelForm):
    # projects = forms.ModelMultipleChoiceField(
    #     queryset=Project.objects.all(),
    #     required=False,
    #     widget=admin.widgets.FilteredSelectMultiple(
    #         'projects',
    #         False,
    #     )
    # )

    class Meta:
        model = AccountRequest
        exclude = ()

    def clean(self):
        # import pdb;pdb.set_trace()
        super(AccountRequestAdminForm,self).clean()
        conditions = [
            self.instance,
            self.instance.status != 'a',
            self.cleaned_data['status'] == 'a'
        ]
        if all(conditions):
            un = self.cleaned_data['username']
            org = self.cleaned_data['organization']
            rc_users = RcLdapUser.objects.filter(username=un)
            for user in rc_users:
                # org formatted as ou=ucb, so it must be parsed
                user_org = user.org.split('=')[-1]
                if user_org == org:
                    raise forms.ValidationError('RC Account already exists: {}'.format(un))

@admin.register(AccountRequest)
class AccountRequestAdmin(admin.ModelAdmin):
    def approve_requests(modeladmin, request, queryset):
        queryset.update(status='a')
    approve_requests.short_description = 'Approve selected account requests'
    # actions = [approve_requests]
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
    form = AccountRequestAdminForm

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
        'effective_uid',
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

    def get_actions(self, request):
        #Disable delete
        actions = super(RcLdapUserAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        org = form.cleaned_data['organization'] or None
        obj.save(organization=org)

# Overrides default admin form for RcLdapGroups to allow
# for filtered multiselect widget.
class RcLdapGroupForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        instance = kwargs.get('instance')
        if instance:
            self.base_fields['organization'].initial = instance.org.split('=')[-1].lower()
            self.base_fields['dn'].widget.attrs['readonly'] = True
            self.base_fields['organization'].widget.attrs['disabled'] = True
        super(RcLdapGroupForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))

        self.fields['gid'].required = False
        self.fields['members'].required = False
        self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Members',
                                        is_stacked=False)
        self.fields['dn'].required = False

    organization = forms.ChoiceField(required=False,choices=ORGANIZATIONS)

    class Meta:
        model = RcLdapGroup
        fields = [
            'dn',
            'organization',
            'name',
            'gid',
            'members',
        ]

@admin.register(RcLdapGroup)
class RcLdapGroupAdmin(admin.ModelAdmin):
    list_display = ['name','effective_cn','gid','members','organization',]
    search_fields = ['name']
    form = RcLdapGroupForm

    def get_actions(self, request):
        #Disable delete
        actions = super(RcLdapGroupAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        org = form.cleaned_data['organization'] or None
        obj.save(organization=org)

admin.site.register(IdTracker)
