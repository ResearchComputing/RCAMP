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
    password = forms.CharField(max_length=255,widget=forms.PasswordInput,required=True)
    department = forms.CharField(max_length=128,required=True)
    role = forms.ChoiceField(choices=REQUEST_ROLES,required=True)

    @sensitive_variables('pw')
    def clean(self):
        cleaned_data = super(AccountRequestUcbForm,self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        organization = 'ucb'
        account_requests = AccountRequest.objects.filter(username=username)
        for aaccount_request in account_requests:
            if org == aaccount_request.organization:
                raise forms.ValidationError(
                    'An account request has already been submitted for {}'.format(username)
                )
        try:
            # rc_users = RcLdapUser.objects.filter(username=username)
            # for user in rc_users:
            #     if org == user.organization.lower():
            #         raise forms.ValidationError(
            #             'An account already exists with username {}'.format(username)
            #         )
            # authed = False
            authed = True
            cu_user = CuLdapUser.objects.get(username=username)
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
    additional_summit_funding = forms.CharField(widget=forms.Textarea,required=False)
    additional_summit_description = forms.CharField(widget=forms.Textarea,required=False)

    # Course follow-up
    additional_course_instructor_email = forms.EmailField(required=False)
    additional_course_course_number = forms.CharField(max_length=48,required=False)
