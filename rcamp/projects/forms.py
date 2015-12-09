from django import forms
from accounts.models import RcLdapUser
from projects.models import ProjectRequest
from projects.models import AllocationRequest


class ProjectRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectRequestForm,self).__init__(*args,**kwargs)
        self.options = [ (u.id,u.first_name+' '+u.last_name+' ('+u.username+')') \
                for u in RcLdapUser.objects.all().order_by('username') ]
    
    class Meta:
        model = ProjectRequest
        fields = [
            'title',
            'principal_investigator',
            'abstract',
            'proposal',
        ]

class AllocationRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AllocationRequestForm,self).__init__(*args,**kwargs)
        self.options = [ (u.id,u.first_name+' '+u.last_name+' ('+u.username+')') \
                for u in RcLdaptUser.objects.all().order_by('username') ]
    
    class Meta:
        model = AllocationRequest
        fields = [
            'title',
            'principal_investigator',
            'abstract',
            'proposal',
            'time_requested',
            'disk_space',
            'software_request',
            'members',
        ]
