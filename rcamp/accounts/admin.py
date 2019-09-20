import logging

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django import forms
from lib.fields import LdapCsvField
from accounts.models import (
    User,
    RcLdapUser,
    CuLdapUser,
    RcLdapGroup,
    IdTracker,
    AccountRequest,
    Intent,
    ORGANIZATIONS
)


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = ['username','organization','first_name','last_name','email']
    search_fields = ['username','first_name','last_name','email']

class AccountRequestAdminForm(forms.ModelForm):
    class Meta:
        model = AccountRequest
        exclude = ()

    def clean(self):
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
                if user.organization == org:
                    raise forms.ValidationError('RC Account already exists: {}'.format(un))

class IntentInline(admin.TabularInline):
    model = Intent

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
    inlines = [IntentInline,]
    form = AccountRequestAdminForm

class RcLdapModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(RcLdapModelForm,self).__init__(*args,**kwargs)
        instance = getattr(self,'instance',None)
        if instance and instance.pk:
            self.fields['organization'].initial = instance.organization.lower()
            self.fields['organization'].widget.attrs['disabled'] = True
            self.fields['dn'].widget.attrs['readonly'] = True
        self.fields['dn'].required = False

    organization = forms.ChoiceField(required=False,choices=ORGANIZATIONS)

    def clean_organization(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.organization
        else:
            return self.cleaned_data['organization']

class RcLdapUserForm(RcLdapModelForm):
    def __init__(self,*args,**kwargs):
        super(RcLdapUserForm,self).__init__(*args,**kwargs)
        try:
            self.initial['role'] = ','.join(self.instance.role)
        except TypeError:
            pass
        try:
            self.initial['affiliation'] = ','.join(self.instance.affiliation)
        except TypeError:
            pass
        self.fields['gecos'].required = False

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

class RcLdapModelAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        #Disable delete
        actions = super(RcLdapModelAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        logger = logging.getLogger('admin')
        logger.info("Saving model")
        try:
            logger.info("Request = ", request)
        except:
            logger.info("No request")
        try:
            logger.info("Obj = ", obj)
        except:
            logger.info("No obj")
        try:
            logger.info("Form = ", form)
        except:
            logger.info("No form")
        try:
            logger.info("Change = ", change)
        except:
            logger.info("No change")

        if obj.pk:
            organization = obj.organization
            logger.info("In if")
            logger.info("In if, obj.pk, organization =", obj.pk, organization)
        else:
            organization = form.cleaned_data['organization']
            logger.info("In else")
            logger.info("else organization = ", organization)


        if organization:
            logger.info("Final organization = ", organization)
        else:
            logger.info("Final no organization")

        obj.save(organization=organization)

@admin.register(RcLdapUser)
class RcLdapUserAdmin(RcLdapModelAdmin):
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
    ]
    ordering = ('last_name',)
    form = RcLdapUserForm

# Overrides default admin form for RcLdapGroups to allow
# for filtered multiselect widget.
class RcLdapGroupForm(RcLdapModelForm):
    def __init__(self,*args,**kwargs):
        super(RcLdapGroupForm,self).__init__(*args,**kwargs)
        instance = getattr(self,'instance',None)
        if instance and instance.pk:
            user_tuple = ((u.username,'%s (%s %s)'%(u.effective_uid,u.first_name,u.last_name))
                for u in RcLdapUser.objects.all().order_by('username') if u.organization == instance.organization.lower())
        else:
            user_tuple = ((u.username,'%s (%s %s)'%(u.effective_uid,u.first_name,u.last_name))
                for u in RcLdapUser.objects.all().order_by('username'))

        self.fields['gid'].required = False
        self.fields['members'].required = False
        self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Members',
                                        is_stacked=False)

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
class RcLdapGroupAdmin(RcLdapModelAdmin):
    list_display = ['name','effective_cn','gid','members','organization',]
    search_fields = ['name']
    form = RcLdapGroupForm

admin.site.register(IdTracker)
