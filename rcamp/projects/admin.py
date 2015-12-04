from django.contrib import admin
from django import forms
from accounts.models import RcLdapUser
from projects.models import Project
from projects.models import Allocation


# Overrides default admin form for Projects to allow
# for filtered multiselect widget.
class ProjectForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(ProjectForm,self).__init__(*args,**kwargs)
        pi_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name)) 
            for u in RcLdapUser.objects.all().order_by('username'))
        alloc_tuple = ((a.allocation_id,'%s (%s)'%(a.allocation_id,a.title)) 
            for a in Allocation.objects.all().order_by('allocation_id'))
        
        self.fields['principal_investigator'].required = False
        self.fields['principal_investigator'].widget = forms.widgets.Select(
                                        choices=pi_tuple)
        self.fields['allocations'].required = False
        self.fields['allocations'].widget = admin.widgets.FilteredSelectMultiple(
                                        choices=alloc_tuple,
                                        verbose_name='Allocations',
                                        is_stacked=False)
    
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
