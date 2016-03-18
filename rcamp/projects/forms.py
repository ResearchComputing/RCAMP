from django import forms
from django.contrib.admin import widgets

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
