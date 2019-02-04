from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from lib.fields import CsvField
from accounts.models import (
    RcLdapUser,
    User
)
from projects.models import (
    Project,
    Allocation,
    AllocationRequest
)



# Overrides default admin form for Projects to allow
# for filtered multiselect widget.
class ProjectAdminForm(forms.ModelForm):
    managers = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            'managers',
            False,
        )
    )
    collaborators = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            'collaborators',
            False,
        )
    )

    def __init__(self,*args,**kwargs):
        super(ProjectAdminForm,self).__init__(*args,**kwargs)
        try:
            self.initial['pi_emails'] = ','.join(self.instance.pi_emails)
        except TypeError:
            pass

    pi_emails = CsvField(required=True)

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
            'notes',
            'parent_account',
            'qos_addenda',
            'deactivated',
        ]

class AllocationInline(admin.TabularInline):
    model = Allocation

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 0
        if obj:
            allocs = Allocation.objects.filter(project=obj)
            if allocs.count() <= 50:
                max_num = 50
        return max_num

class AllocationRequestInline(admin.TabularInline):
    model = AllocationRequest

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 0
        if obj:
            ars = AllocationRequest.objects.filter(project=obj)
            if ars.count() <= 50:
                max_num = 50
        return max_num

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
    ]
    search_fields = [
        'project_id',
        'pi_emails',
        'organization',
        'title',
        'qos_addenda',
        'created_on',
    ]
    inlines = [
        AllocationInline,
        AllocationRequestInline,
    ]

    form = ProjectAdminForm

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = [
        'allocation_id',
        'amount',
        'start_date',
        'end_date',
        'created_on',
    ]

    list_editable = [
        'amount',
        'start_date',
        'end_date',
    ]

@admin.register(AllocationRequest)
class AllocationRequestAdmin(admin.ModelAdmin):
    def approve_requests(modeladmin, request, queryset):
        queryset.update(status='a')
    approve_requests.short_description = 'Approve selected allocation requests'
    actions = [approve_requests]
    list_display = [
        'pk',
        'project_link',
        'request_date',
        'time_requested',
        'status',
        'approved_on',
        'requester',
    ]

    list_editable = [
        'status',
    ]

    readonly_fields = ('project_link',)

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:projects_project_change", args=(obj.project.pk,)),
            obj.project.project_id
        ))
    project_link.short_description = 'project_link'
