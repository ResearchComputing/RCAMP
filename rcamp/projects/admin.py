from django.contrib import admin
from django import forms
from accounts.models import RcLdapUser
from projects.models import Project



# Overrides default admin form for Projects to allow
# for filtered multiselect widget.
class ProjectAdminForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(ProjectAdminForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))
        self.fields['managers'].required = False
        self.fields['managers'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Managers',
                                        is_stacked=False)

        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))
        self.fields['collaborators'].required = False
        self.fields['collaborators'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Collaborators',
                                        is_stacked=False)

    class Meta:
        model = Project
        fields = [
            'project_id',
            'description',
            'title',
            'pi_emails',
            'managers',
            'collaborators',
            'organization',
            # 'created_on',
            'notes',
            'qos_addenda',
            'deactivated',
        ]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # filter_horizontal = ('allocations',)
    list_display = [
        'project_id',
        'pi_emails',
        'organization',
        'title',
        'created_on',
        'qos_addenda',
        'deactivated',
        # 'current_limit',
    ]
    search_fields = [
        'project_id',
        'pi_emails',
        'organization',
        'title',
        'qos_addenda',
        'created_on',
    ]
    form = ProjectAdminForm

# Overrides default admin form for Allocations to allow
# for filtered multiselect widget.
# class AllocationForm(forms.ModelForm):
#     def __init__(self,*args,**kwargs):
#         super(AllocationForm,self).__init__(*args,**kwargs)
#         user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
#             for u in RcLdapUser.objects.all().order_by('username'))
#
#         self.fields['members'].required = False
#         self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
#                                         choices=user_tuple,
#                                         verbose_name='Members',
#                                         is_stacked=False)
#
#     class Meta:
#         model = Allocation
#         fields = [
#             'allocation_id',
#             'title',
#             'cpu_mins_awarded',
#             'members',
#         ]
#
# @admin.register(Allocation)
# class AllocationAdmin(admin.ModelAdmin):
#     list_display = [
#         'allocation_id',
#         'title',
#         'cpu_mins_awarded',
#         'created_on',
#     ]
#     search_fields = [
#         'allocation_id',
#         'title',
#         'cpu_mins_awarded',
#         'created_on',
#         'members',
#     ]
#     form = AllocationForm

# Overrides default admin form for AllocationRequests to allow
# for filtered multiselect widget.
# class AllocationRequestForm(forms.ModelForm):
#     def __init__(self,*args,**kwargs):
#         super(AllocationRequestForm,self).__init__(*args,**kwargs)
#         user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
#             for u in RcLdapUser.objects.all().order_by('username'))
#
#         self.fields['members'].required = False
#         self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
#                                         choices=user_tuple,
#                                         verbose_name='Members',
#                                         is_stacked=False)
#
#     class Meta:
#         model = AllocationRequest
#         fields = [
#             'title',
#             'abstract',
#             'funding',
#             'proposal',
#             'time_requested',
#             'cpu_mins_awarded',
#             'disk_space',
#             'software_request',
#             'members',
#             'status',
#             'approved_on',
#             'notes',
#             'project',
#             'requester',
#         ]
#
# @admin.register(AllocationRequest)
# class AllocationRequestAdmin(admin.ModelAdmin):
#     def approve_requests(modeladmin, request, queryset):
#         queryset.update(status='a')
#     approve_requests.short_description = 'Approve selected allocation requests'
#     actions = [approve_requests]
#     list_display = [
#         'title',
#         'project',
#         'time_requested',
#         'status',
#         'request_date',
#     ]
#     search_fields = [
#         'title',
#         'project',
#         'request_date',
#     ]
#     form = AllocationRequestForm
