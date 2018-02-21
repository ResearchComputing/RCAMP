from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.views.decorators.debug import sensitive_variables
from accounts.models import (
    CuLdapUser,
    CsuLdapUser,
    RcLdapUser,
    AccountRequest,
    REQUEST_ROLES
)



class AccountRequestUcbForm(forms.Form):
    username = forms.CharField(max_length=48,required=True)
    password = forms.CharField(max_length=255,widget=forms.PasswordInput)

    role = forms.ChoiceField(choices=REQUEST_ROLES)

    @sensitive_variables('pw')
    def clean(self):
        cleaned_data = super(AccountRequestUcbForm,self).clean()
        un = cleaned_data.get('username')
        pw = cleaned_data.get('password')
        org = 'ucb'
        ars = AccountRequest.objects.filter(username=un)
        for ar in ars:
            if org == ar.organization:
                raise forms.ValidationError(
                    'An account request has already been submitted for {}'.format(un)
                )
        try:
            # rcu = RcLdapUser.objects.filter(username=un)
            # for u in rcu:
            #     user_org = u.org.split('=')[-1]
            #     if org == user_org.lower():
            #         raise forms.ValidationError(
            #             'An account already exists with username {}'.format(un)
            #         )
            # authed = False
            authed = True
            user = CuLdapUser.objects.get(username=un)
            # authed = user.authenticate(pw)
            if not authed:
                raise forms.ValidationError('Invalid password')
            return cleaned_data
        except UnboundLocalError:
            raise forms.ValidationError('Invalid organization')
        except CuLdapUser.DoesNotExist:
            raise forms.ValidationError('Invalid username')
        except TypeError:
            raise forms.ValidationError('Missing field(s)')


class AccountRequestIntentForm(forms.Form):
    reason_summit = forms.BooleanField()
    reason_course = forms.BooleanField()
    reason_petalibrary = forms.BooleanField()
    reason_blanca = forms.BooleanField()

    # Summit additional info
    additional_summit_pi_email = forms.EmailField(required=False)
    additional_summit_title = forms.CharField(max_length=128,required=False)
    additional_summit_funding = forms.CharField(widget=forms.Textarea,required=False)
    additional_summit_description = forms.CharField(widget=forms.Textarea,required=False)

    # Course follow-up
    additional_course_instructor_email = forms.EmailField(required=False)
    additional_course_course_number = forms.CharField(max_length=48,required=False)
