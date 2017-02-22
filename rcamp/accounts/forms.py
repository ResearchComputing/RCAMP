from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.views.decorators.debug import sensitive_variables
from accounts.models import CuLdapUser
from accounts.models import CsuLdapUser
from accounts.models import RcLdapUser
from accounts.models import AccountRequest
from accounts.models import SHELL_CHOICES
from accounts.models import REQUEST_ROLES
from projects.models import Project



class AccountRequestForm(forms.Form):
    ORGS = (
        ('ucb','University of Colorado Boulder'),
        ('csu','Colorado State University'),
        # ('xsede','XSEDE'),
    )
    organization = forms.ChoiceField(choices=ORGS,required=True)
    username = forms.CharField(max_length=12,required=True)
    password = forms.CharField(max_length=255,widget=forms.PasswordInput)

    role = forms.ChoiceField(choices=REQUEST_ROLES)
    login_shell = forms.ChoiceField(required=False,choices=SHELL_CHOICES)

    blanca = forms.BooleanField(required=False)
    janus = forms.BooleanField(required=False)
    summit = forms.BooleanField(required=False)
    petalibrary_active = forms.BooleanField(required=False)
    petalibrary_archive = forms.BooleanField(required=False)

    @sensitive_variables('pw')
    def clean(self):
        cleaned_data = super(AccountRequestForm,self).clean()
        un = cleaned_data.get('username')
        pw = cleaned_data.get('password')
        org = cleaned_data.get('organization')
        ars = AccountRequest.objects.filter(username=un)
        for ar in ars:
            if org == ar.organization:
                raise forms.ValidationError(
                    'An account request has already been submitted for {}'.format(un)
                )
        try:
            rcu = RcLdapUser.objects.filter(username=un)
            for u in rcu:
                user_org = u.org.split('=')[-1]
                if org == user_org.lower():
                    raise forms.ValidationError(
                        'An account already exists with username {}'.format(un)
                    )
            authed = False
            if org == 'ucb':
                user = CuLdapUser.objects.get(username=un)
                authed = user.authenticate(pw)
            elif org == 'csu':
                user = CsuLdapUser.objects.get(username=un)
                authed = user.authenticate(pw)
            elif org == 'xsede':
                pass
            if not authed:
                raise forms.ValidationError('Invalid password')
            return cleaned_data
        except UnboundLocalError:
            raise forms.ValidationError('Invalid organization')
        except CuLdapUser.DoesNotExist:
            raise forms.ValidationError('Invalid username')
        except CsuLdapUser.DoesNotExist:
            raise forms.ValidationError('Invalid username')
        except TypeError:
            raise forms.ValidationError('Missing field(s)')

class SponsoredAccountRequestForm(AccountRequestForm):
    sponsor_email = forms.EmailField(required=True)

    class Meta:
        exclude = (
            'organization',
            'role',
        )

    def __init__ (self, data=None, **kwargs):
        if data is not None:
            data['organization'] = 'ucb'
            data['role'] = 'sponsored'
        super(SponsoredAccountRequestForm, self).__init__(data=data, **kwargs)

class ClassAccountRequestForm(AccountRequestForm):
    course_number = forms.CharField(max_length=32,required=True)

    class Meta:
        exclude = (
            'organization',
            'role',
        )

    def __init__ (self, data=None, **kwargs):
        if data is not None:
            data['organization'] = 'ucb'
            data['role'] = 'student'
        super(ClassAccountRequestForm, self).__init__(data=data, **kwargs)

class ProjectAccountRequestForm(AccountRequestForm):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        required=True,
        widget=FilteredSelectMultiple(
            'Projects',
            False,
        ))

    class Meta:
        exclude = (
            'blanca',
            'janus',
            'summit',
            'petalibrary_active',
            'petalibrary_archive',
        )
