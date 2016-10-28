from django import forms
from django.contrib.admin import widgets

from lib.fields import MultiEmailField
from accounts.models import RcLdapUser
from projects.models import Project


def get_user_choices ():
    for user in RcLdapUser.objects.all().order_by('username'):
        user_display = '{0} ({1} {2})'.format(
            user.username, user.first_name, user.last_name)
        yield (user.username, user_display)


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

        widgets = {
            'managers': widgets.FilteredSelectMultiple(
                verbose_name='Managers', is_stacked=False),
            'collaborators': widgets.FilteredSelectMultiple(
                verbose_name='Collaborators', is_stacked=False),
        }

    pi_emails = MultiEmailField(required=True)
    managers = forms.MultipleChoiceField(choices=get_user_choices, required=False)
    collaborators = forms.MultipleChoiceField(choices=get_user_choices, required=False)


class ProjectEditForm(forms.Form):

    title = forms.CharField(max_length=256,required=True)
    description = forms.CharField(widget=forms.Textarea,required=True)
    pi_emails = MultiEmailField(required=True)
    managers = forms.MultipleChoiceField(
        choices=get_user_choices,
        widget=widgets.FilteredSelectMultiple(
                verbose_name='Managers', is_stacked=False),
        required=False,
    )
    collaborators = forms.MultipleChoiceField(
        choices=get_user_choices,
        widget=widgets.FilteredSelectMultiple(
            verbose_name='Collaborators', is_stacked=False),
        required=False,
    )


class ReferenceForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea,required=True)
    link = forms.CharField(widget=forms.Textarea,required=True)

class AllocationRequestForm(forms.Form):
    VALID_DOC_TYPES = ['application/msword', 'application/pdf', 'text/plain','application/vnd.openxmlformats-officedocument.wordprocessingml.document']

    abstract = forms.CharField(widget=forms.Textarea,required=True)
    funding = forms.CharField(widget=forms.Textarea,required=True)
    proposal = forms.FileField(required=True)
    time_requested = forms.IntegerField(min_value=0,required=True)
    disk_space = forms.IntegerField(min_value=0,required=False)
    software_request = forms.CharField(widget=forms.Textarea,required=False)

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
