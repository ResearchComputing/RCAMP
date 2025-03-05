import logging

from django.contrib import admin, messages
from django.contrib.auth import admin as auth_admin
from django import forms
from lib.fields import LdapCsvField
from accounts.models import (
    User,
    RcLdapUser,
    CuLdapUser,
    RcLdapGroup,
    IdTracker,
    ComanageUser,
    ComanageGroup,
    AccountRequest,
    Intent,
    ORGANIZATIONS
)
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import ComanageSyncForm
from .models import ComanageUser
from comanage.lib import UserCO
from lib.utils import get_user_and_groups, get_comanage_users_by_org
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
    list_display = ['name','effective_cn','gid','members','organization',]
    search_fields = ['name']
    form = RcLdapGroupForm

# Custom action to sync users from Comanage
def sync_users_from_comanage(modeladmin, request, queryset):
    """
    Sync the selected users from Comanage.
    """
    if not queryset:
        users = ["kyre0001_amc"]
        for user in users:
            # try:
            #     ComanageUser.sync_from_comanage(user.user_id)  # Call the sync method on the user
            #     modeladmin.message_user(request, f"User {user.name} synced successfully!")
            # except Exception as e:
            #     modeladmin.message_user(request, f"Error syncing user {user.name}: {str(e)}", level='debug')
            try:
                ComanageUser.sync_from_comanage(user)  # Call the sync method on the user
                modeladmin.message_user(request, f"User {user} synced successfully!")
            except Exception as e:
                modeladmin.message_user(request, f"Error syncing user {user}: {str(e)}", level='debug')

# Action to sync users in bulk
def sync_users_from_comanage(modeladmin, request, queryset):
    """
    Sync the selected users from Comanage.
    """
    if queryset.count() == 0:
        modeladmin.message_user(request, "No users selected to sync.", level=messages.WARNING)
        return

    for user in queryset:
        try:
            # Assuming ComanageUser.sync_from_comanage expects user ID
            ComanageUser.sync_from_comanage(user.user_id)  # Sync logic here
            modeladmin.message_user(request, f"User {user.name} synced successfully!", level=messages.SUCCESS)
        except Exception as e:
            modeladmin.message_user(request, f"Error syncing user {user.name}: {str(e)}", level=messages.ERROR)

# ComanageUserAdmin with additional customization and sync functionality
class ComanageUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name', 'email', 'co_person_id']
    search_fields = ['user_id', 'name', 'email', 'co_person_id']
    readonly_fields = ['user_id', 'name', 'email', 'co_person_id', 'group_names', 'created_at', 'modified']
    actions = [sync_users_from_comanage]

    # Disable the "Add" button in the list view
    def has_add_permission(self, request):
        return False

    # Disable the delete button for individual objects
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """
        Override the changelist view to trigger a function when the list of users is accessed.
        """
        # Call your custom function here (e.g., sync users from Comanage)
        try:
            user = "kyre0001_amc"  # Or you can filter users as needed
            ComanageUser.sync_from_comanage(user)  # Call your sync function here
            self.message_user(request, "Users synced successfully!", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error syncing users: {str(e)}", level=messages.ERROR)

        # Proceed with the normal changelist view rendering
        return super().changelist_view(request, extra_context)

    # Override the change_view method to remove the "Save" button and show custom sync button
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False

        return super().change_view(request, object_id, form_url, extra_context)

# class ComanageUserAdmin(admin.ModelAdmin):
#     list_display = ['user_id', 'name', 'email', 'co_person_id']
#     search_fields = ['user_id', 'name', 'email', 'co_person_id']
#     readonly_fields = ['user_id', 'name', 'email', 'co_person_id', 'group_names', 'created_at', 'modified',]
#     actions = [sync_users_from_comanage]

#     # Disable the "Add" button in the list view
#     def has_add_permission(self, request):
#         return False

#     # Disable the delete button for individual objects
#     def has_delete_permission(self, request, obj=None):
#         return False

#     # Override the change_view method to remove the "Save" button
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['show_save_and_add_another'] = False
#         extra_context['show_save_and_continue'] = False
#         extra_context['show_save'] = False
#         return super().change_view(request, object_id, form_url, extra_context)

    # Optionally, you can define a custom form (not shown here)
    # form = CustomUserForm  # Uncomment and define your form if necessary

# class ComanageSyncAdmin(admin.ModelAdmin):
#     change_list_template = "comanage_sync_list.html"  # Custom template for the changelist page
#     list_display = ('user_id', 'name', 'email', 'created_at', 'modified', 'actions')
#     search_fields = ['user_id', 'name', 'email']
#     actions = ['custom_action'] 

#     def changelist_view(self, request, extra_context=None):
#         search_query = request.GET.get('q', '') 
        
#         # Filter user data if there is a search query
#         if search_query:
#             user_data = ComanageUser.objects.filter(
#                 Q(user_id__icontains=search_query) | Q(email__icontains=search_query)
#             )
#         else:
#             # Fetch all user data if no search query is provided
#             user_data = ComanageUser.objects.all()

#         # Add user data to the context for rendering
#         extra_context = extra_context or {}
#         extra_context['user_data'] = user_data
#         extra_context['search_query'] = search_query  # Optional: to display the query in the search bar

#         # Render the custom changelist view with the extra context
#         return super().changelist_view(request, extra_context=extra_context)

#     # Define custom URL for detailed group view
#     def get_urls(self):
#         # Get default admin URLs
#         urls = super().get_urls()

#         # Add custom URL for sync users and user detail view
#         custom_urls = [
#             path('sync-users/', self.admin_site.admin_view(self.sync_multiple_users), name='comanage-sync-users'),
#             path('comanage-sync/<str:user_id>/view-groups/', self.admin_site.admin_view(self.view_groups), name='comanage-sync-view-groups'),
#             path('comanage-sync/<str:user_id>/', self.admin_site.admin_view(self.comanage_sync_view), name='comanage-sync-user-detail'),
#         ]
#         return custom_urls + urls

#     # View to show detailed user info and groups
#     def comanage_sync_view(self, request, user_id):
#         # Fetch user and group data based on user_id
#         user_data, groups = get_user_and_groups(user_id)  # You need to implement this function

#         # Render the user detail page with user data and groups
#         return render(request, 'comanage_sync_detail.html', {
#             'user_data': user_data,
#             'groups': groups,
#         })

#     # Function to handle syncing multiple users
#     def sync_multiple_users(self, request):
#         # Define your list of user_ids to sync

#         user_data = get_comanage_users_by_org()

#         # Sync users from Comanage
#         for user in user_data:
#             ComanageUser.sync_from_comanage(user.cuhpcuid)  # Sync method for updating users

#         # Redirect back to the changelist view after sync is complete
#         self.message_user(request, "Users have been synced successfully!")
#         url = reverse('admin:accounts_comanageuser_changelist')

#         return redirect(url)  # Update this URL if necessary

#     # Add actions to your admin class to display a custom button
#     def changelist_actions(self, request):
#         # Custom button that will trigger the sync function
#         return format_html('<a class="button" href="{}">Sync Users</a>', 
#             self.admin_site.urls['comanage-sync-users']
#         )

#     def custom_action(self, obj):
#         # Add "View Groups" link for each user
#         return format_html('<a href="{}" class="button">View Groups</a>',
#             reverse('admin:comanage-sync-user-detail', args=[obj.user_id])
#         )
        
#     def view_groups(self, request, user_id):
#         try:
#             # Fetch the user based on user_id
#             user = ComanageUser.objects.get(user_id=user_id)
            
#             # Fetch the user's groups, assuming you have a `groups` field or relation in your model
#             user_groups = user.groups.all()

#             # Get members of each group (assuming there's a Many-to-Many or ForeignKey relationship with users)
#             group_members = {}
#             for group in user_groups:
#                 group_members[group.name] = group.members.all()  # Adjust based on your Group model

#             return render(request, 'view_groups.html', {
#                 'user': user,
#                 'user_groups': user_groups,
#                 'group_members': group_members,
#             })

#         except ComanageUser.DoesNotExist:
#             raise Http404("User not found")

class ComanageGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ComanageGroupForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        group_members = None

        if instance and instance.pk:
            # If the group instance exists, filter out the members already in the group
            group_members = instance.members.all()
            available_users = ComanageUser.objects.all()
        else:
            # If this is a new group, show all users
            available_users = ComanageUser.objects.all()

        # Prepare choices for the 'members' field (users not already in the group)
        user_choices = [
            (user.id, f'{user.name} ({user.user_id})') for user in available_users
        ]

        # Set pre-selected members based on the group instance
        self.fields['members'].initial = group_members

        # Set the required fields
        self.fields['gid'].required = False
        self.fields['members'].required = False

        # Apply the filtered multi-select widget
        self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
            verbose_name='Members',
            is_stacked=False
        )

        # Assign the available choices dynamically
        self.fields['members'].choices = user_choices

    class Meta:
        model = ComanageGroup
        fields = ['name', 'group_id', 'gid', 'created_at', 'modified', 'members']

class ComanageGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'gid', 'get_members']
    search_fields = ['name', 'group_id', 'gid']
    readonly_fields = ['group_id', 'created_at', 'modified']
    form = ComanageGroupForm

    # Custom method to display group members
    def get_members(self, obj):
        """
        Custom method to display all members of the group in the admin list view.
        """
        return ", ".join([user.name for user in obj.members.all()])

    get_members.short_description = 'Group Members'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Optionally, modify the queryset if needed
        return queryset

admin.site.register(ComanageGroup, ComanageGroupAdmin)
admin.site.register(ComanageUser, ComanageUserAdmin)

admin.site.register(IdTracker)
