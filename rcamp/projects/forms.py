from django import forms
from django.contrib import admin

from lib.fields import MultiEmailField
from accounts.models import (
    RcLdapUser,
    User
)
from projects.models import Project


class ProjectMembersModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return u'{} ({} {})'.format(obj.username,obj.first_name,obj.last_name)

class ProjectForm(forms.ModelForm):

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

    pi_emails = MultiEmailField(required=True)
    managers = ProjectMembersModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            'managers',
            False,
        )
    )
    collaborators = ProjectMembersModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            'collaborators',
            False,
        )
    )

class ProjectEditForm(ProjectForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'pi_emails',
            'managers',
            'collaborators',
        ]

class ReferenceForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea,required=True)
    link = forms.CharField(widget=forms.Textarea,required=True)

class AllocationRequestForm(forms.Form):
    VALID_DOC_TYPES = ['application/msword', 'application/pdf', 'text/plain','application/vnd.openxmlformats-officedocument.wordprocessingml.document']

    proposal = forms.FileField(required=True)

    def clean(self):
        cleaned_data = super(AllocationRequestForm,self).clean()
        proposal = cleaned_data.get('proposal')
        err_proposal = []
        if proposal:
            if proposal.size > (1024**2) * 10:
                err_proposal += ['File size over 10MB']
            if proposal.content_type not in self.VALID_DOC_TYPES:
                err_proposal += ['Invalid file type. Must be a PDF, DOC, DOCX, or TXT.']
            if len(err_proposal) > 0:
                self._errors['proposal'] = self.error_class(err_proposal)

        return cleaned_data

class StartupRequestForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea,required=True)
    disk_space = forms.IntegerField(min_value=0,required=False)
    software_request = forms.CharField(widget=forms.Textarea,required=False)
