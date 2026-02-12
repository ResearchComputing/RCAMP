import logging

from django.contrib import admin, messages
from django.contrib.auth import admin as auth_admin
from django import forms
from django.http import Http404
from lib.fields import LdapCsvField
from ldap.filter import escape_filter_chars
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
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.admin.utils import quote, unquote
#from .forms import ComanageSyncForm
#from .models import ComanageUser
#from comanage.lib import UserCO
# from lib.utils import get_user_and_groups, get_comanage_users_by_org
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db.models import Q


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
        'discipline',
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

        if obj.pk and obj.organization:
            organization = obj.organization
        else:
            organization = form.cleaned_data['organization']

        logger.info("Saving {obj} with organization {org}".format(obj=obj, org=organization))

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
    list_display = ['dn_display','name','effective_cn','gid','members','organization']
    # Make the DN column the clickable link
    list_display_links = ['dn_display']

    # Optional: allow finding by DN substring (see §3)
    search_fields = ['name']  # 'dn' is not a DB field; handled in get_search_results

    form = RcLdapGroupForm

    # Column that shows the DN (human readable)
    def dn_display(self, obj):
        return obj.dn
    dn_display.short_description = "DN"

    # Ensure changelist links use DN (unique)
    def url_for_result(self, result):
        return reverse("admin:accounts_rcldapgroup_change", args=(quote(result.dn),))

    # Keep your DN-aware get_object (from earlier)
    def get_object(self, request, object_id, from_field=None):
        dn = unquote(object_id)
        if "=" in dn and "," in dn:
            try:
                return self.model.objects.get(dn=dn)
            except self.model.DoesNotExist:
                return None
        # Old name-based URL fallback (handle duplicates cleanly)
        qs = self.get_queryset(request).filter(name=object_id)
        count = qs.count()
        if count == 1:
            return qs.first()
        elif count == 0:
            return None
        else:
            raise Http404(
                f"Multiple groups named {object_id!r}. "
                "Open from the changelist (which uses DN) to pick the exact entry."
            )
    
    def get_search_results(self, request, queryset, search_term):   
        """
        Restrict search to:
          - LDAP-side: name (cn) substring
          - Client-side: DN substring
        Then return a queryset filtered by OR of exact names of all matches.
        Avoid any pk/dn lookups to prevent 'Unsupported dn lookup: in'.
        """
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        if not search_term:
            return qs, use_distinct

        term = search_term.strip()
        term_escaped = escape_filter_chars(term)
        term_lower = term.lower()

        # 1) LDAP-side: cn contains
        try:
            name_qs = queryset.filter(name__contains=term_escaped)
            names_from_name = set(name_qs.values_list('name', flat=True))
        except Exception:
            names_from_name = set()

        # 2) Client-side: DN substring (iterate the queryset and test obj.dn)
        try:
            names_from_dn = {obj.name for obj in queryset if term_lower in obj.dn.lower()}
        except Exception:
            names_from_dn = set()

        # 3) Merge names and filter by OR of exact name matches (no DN lookups)
        names = names_from_name | names_from_dn
        if not names:
            return queryset.none(), use_distinct

        # Build a single OR expression: (cn=name1) OR (cn=name2) OR ...
        q = Q()
        for n in names:
            q |= Q(name=n)
        qs = queryset.filter(q)
        return qs, use_distinct

    # Optional: redirect old name-only URLs to the DN URL when unique
    def change_view(self, request, object_id, form_url='', extra_context=None):
        dn_or_name = unquote(object_id)
        is_dn = ("=" in dn_or_name and "," in dn_or_name)

        if not is_dn:
            qs = self.get_queryset(request).filter(name=dn_or_name)
            if qs.count() == 1:
                obj = qs.first()
                canonical = reverse("admin:accounts_rcldapgroup_change", args=(quote(obj.dn),))
                if request.GET:
                    canonical = f"{canonical}?{request.META.get('QUERY_STRING','')}"
                return HttpResponseRedirect(canonical)

        return super().change_view(request, object_id, form_url, extra_context)



# # Custom action to sync users from Comanage
# def sync_users_from_comanage(modeladmin, request, queryset):
#     """
#     Sync the selected users from Comanage.
#     """
#     if not queryset:
#         users = ["kyre0001_amc", "etda0001", kr]
#         for user in users:
#             try:
#                 ComanageUser.sync_from_comanage(user)  # Call the sync method on the user
#                 modeladmin.message_user(request, f"User {user} synced successfully!")
#             except Exception as e:
#                 modeladmin.message_user(request, f"Error syncing user {user}: {str(e)}", level='debug')

# # Action to sync users in bulk
# def sync_users_from_comanage(modeladmin, request, queryset):
#     """
#     Sync the selected users from Comanage.
#     """
#     if queryset.count() == 0:
#         modeladmin.message_user(request, "No users selected to sync.", level=messages.WARNING)
#         return

#     for user in queryset:
#         try:
#             # Assuming ComanageUser.sync_from_comanage expects user ID
#             ComanageUser.sync_from_comanage(user.user_id)  # Sync logic here
#             modeladmin.message_user(request, f"User {user.name} synced successfully!", level=messages.SUCCESS)
#         except Exception as e:
#             modeladmin.message_user(request, f"Error syncing user {user.name}: {str(e)}", level=messages.ERROR)

# # ComanageUserAdmin with additional customization and sync functionality
# class ComanageUserAdmin(admin.ModelAdmin):
#     list_display = ['user_id', 'name', 'email', 'co_person_id']
#     search_fields = ['user_id', 'name', 'email', 'co_person_id']
#     readonly_fields = ['user_id', 'name', 'email', 'co_person_id', 'group_names', 'created_at', 'modified']
#     actions = [sync_users_from_comanage]

#     # Disable the "Add" button in the list view
#     def has_add_permission(self, request):
#         return False

#     # Disable the delete button for individual objects
#     def has_delete_permission(self, request, obj=None):
#         return False
    
#     def changelist_view(self, request, extra_context=None):
#         """
#         Override the changelist view to trigger a function when the list of users is accessed.
#         """
#         # Call your custom function here (e.g., sync users from Comanage)
#         try:
#             user = "kyre0001_amc"  # Or you can filter users as needed
#             ComanageUser.sync_from_comanage(user)  # Call your sync function here
#             self.message_user(request, "Users synced successfully!", level=messages.SUCCESS)
#         except Exception as e:
#             self.message_user(request, f"Error syncing users: {str(e)}", level=messages.ERROR)

#         # Proceed with the normal changelist view rendering
#         return super().changelist_view(request, extra_context)

#     # Override the change_view method to remove the "Save" button and show custom sync button
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['show_save_and_add_another'] = False
#         extra_context['show_save_and_continue'] = False
#         extra_context['show_save'] = False

#         return super().change_view(request, object_id, form_url, extra_context)

# class ComanageGroupForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(ComanageGroupForm, self).__init__(*args, **kwargs)
#         instance = getattr(self, 'instance', None)
#         group_members = None

#         if instance and instance.pk:
#             # If the group instance exists, filter out the members already in the group
#             group_members = instance.members.all()
#             available_users = ComanageUser.objects.all()
#         else:
#             # If this is a new group, show all users
#             available_users = ComanageUser.objects.all()

#         # Prepare choices for the 'members' field (users not already in the group)
#         user_choices = [
#             (user.id, f'{user.name} ({user.user_id})') for user in available_users
#         ]

#         # Set pre-selected members based on the group instance
#         self.fields['members'].initial = group_members

#         # Set the required fields
#         self.fields['gid'].required = False
#         self.fields['members'].required = False

#         # Apply the filtered multi-select widget
#         self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
#             verbose_name='Members',
#             is_stacked=False
#         )

#         # Assign the available choices dynamically
#         self.fields['members'].choices = user_choices

#     class Meta:
#         model = ComanageGroup
#         fields = ['name', 'group_id', 'gid', 'created_at', 'modified', 'members']

# class ComanageGroupAdmin(admin.ModelAdmin):
#     list_display = ['name', 'gid', 'get_members']
#     search_fields = ['name', 'group_id', 'gid']
#     readonly_fields = ['group_id', 'created_at', 'modified']
#     form = ComanageGroupForm

#     # Custom method to display group members
#     def get_members(self, obj):
#         """
#         Custom method to display all members of the group in the admin list view.
#         """
#         return ", ".join([user.name for user in obj.members.all()])

#     get_members.short_description = 'Group Members'

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         # Optionally, modify the queryset if needed
#         return queryset

# admin.site.register(ComanageGroup, ComanageGroupAdmin)
# admin.site.register(ComanageUser, ComanageUserAdmin)

admin.site.register(IdTracker)
