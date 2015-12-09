from django.contrib import admin
from django import forms
from accounts.models import RcLdapUser
from projects.models import Project
from projects.models import Allocation
from projects.models import ProjectType
from projects.models import ProjectRequest
from projects.models import AllocationRequest


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = [
        'long_name',
        'short_name',
    ]
    search_fields = [
        'long_name',
        'short_name',
    ]

# Overrides default admin form for Projects to allow
# for filtered multiselect widget.
class ProjectForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(ProjectForm,self).__init__(*args,**kwargs)
        pi_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name)) 
            for u in RcLdapUser.objects.all().order_by('username'))
        
        self.fields['principal_investigator'].required = False
        self.fields['principal_investigator'].widget = forms.widgets.Select(
                                        choices=pi_tuple)
    
    class Meta:
        model = Project
        fields = [
            'project_type',
            'project_id',
            'principal_investigator',
            'title',
            'notes',
            'allocations',
        ]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    filter_horizontal = ('allocations',)
    list_display = [
        'project_id',
        'principal_investigator',
        'title',
        'created_on',
    ]
    search_fields = [
        'project_id',
        'principal_investigator',
        'title',
        'allocations',
        'created_on',
    ]
    form = ProjectForm

# Overrides default admin form for Allocations to allow
# for filtered multiselect widget.
class AllocationForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(AllocationForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name)) 
            for u in RcLdapUser.objects.all().order_by('username'))
        
        self.fields['members'].required = False
        self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Members',
                                        is_stacked=False)
    
    class Meta:
        model = Allocation
        fields = [
            'allocation_id',
            'title',
            'award',
            'members',
        ]

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = [
        'allocation_id',
        'title',
        'award',
        'created_on',
    ]
    search_fields = [
        'allocation_id',
        'title',
        'award',
        'created_on',
        'members',
    ]
    form = AllocationForm

@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'principal_investigator',
        'status',
        'request_date',
    ]
    search_fields = [
        'title',
        'principal_investigator',
        'request_date',
    ]

# Overrides default admin form for AllocationRequests to allow
# for filtered multiselect widget.
class AllocationRequestForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(AllocationRequestForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name)) 
            for u in RcLdapUser.objects.all().order_by('username'))
        
        self.fields['members'].required = False
        self.fields['members'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Members',
                                        is_stacked=False)
    
    class Meta:
        model = AllocationRequest
        fields = [
            'title',
            'abstract',
            'funding',
            'proposal',
            'time_requested',
            'time_awarded',
            'disk_space',
            'software_request',
            'members',
            'status',
            'approved_on',
            'notes',
            'project',
            'requester',
        ]

@admin.register(AllocationRequest)
class AllocationRequestAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'project',
        'time_requested',
        'status',
        'request_date',
    ]
    search_fields = [
        'title',
        'project',
        'request_date',
    ]
    form = AllocationRequestForm
