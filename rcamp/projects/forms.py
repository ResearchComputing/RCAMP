from django import forms
from django.contrib.admin import widgets

from lib.fields import MultiEmailField
from accounts.models import RcLdapUser
from projects.models import Project



class ProjectForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(ProjectForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))
        self.fields['managers'].required = False
        self.fields['managers'].widget = widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Managers',
                                        is_stacked=False)

        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))
        self.fields['collaborators'].required = False
        self.fields['collaborators'].widget = widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Collaborators',
                                        is_stacked=False)

    pi_emails = MultiEmailField(required=True)

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'pi_emails',
            'managers',
            'collaborators',
            'organization',
        ]

class ProjectEditForm(forms.Form):
    def __init__(self,*args,**kwargs):
        super(ProjectEditForm,self).__init__(*args,**kwargs)
        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))
        self.fields['managers'].required = False
        self.fields['managers'].widget = widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Managers',
                                        is_stacked=False)

        user_tuple = ((u.username,'%s (%s %s)'%(u.username,u.first_name,u.last_name))
            for u in RcLdapUser.objects.all().order_by('username'))
        self.fields['collaborators'].required = False
        self.fields['collaborators'].widget = widgets.FilteredSelectMultiple(
                                        choices=user_tuple,
                                        verbose_name='Collaborators',
                                        is_stacked=False)

    title = forms.CharField(max_length=256,required=True)
    description = forms.CharField(widget=forms.Textarea,required=True)
    pi_emails = MultiEmailField(required=True)
    managers = forms.CharField(max_length=2048)
    collaborators = forms.CharField(max_length=2048)

class ReferenceForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea,required=True)
    link = forms.CharField(widget=forms.Textarea,required=True)

class AllocationRequestForm(forms.Form):
    abstract = forms.CharField(widget=forms.Textarea,required=True)
    funding = forms.CharField(widget=forms.Textarea,required=True)
    proposal = forms.FileField(required=True)
    time_requested = forms.IntegerField(min_value=0,required=True)
    disk_space = forms.IntegerField(min_value=0,required=False)
    software_request = forms.CharField(widget=forms.Textarea,required=False)

class StartupRequestForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea,required=True)
    disk_space = forms.IntegerField(min_value=0,required=False)
    software_request = forms.CharField(widget=forms.Textarea,required=False)
