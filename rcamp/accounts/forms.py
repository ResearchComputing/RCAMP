from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.views.decorators.debug import sensitive_variables
from lib.ldap_utils import get_suffixed_username
from accounts.models import (
    CuLdapUser,
    CsuLdapUser,
    RcLdapUser,
    AccountRequest,
    REQUEST_ROLES
)



class AccountRequestVerifyForm(forms.Form):
    """
    An abstract form for verifying user credentials against a configured authority
    LDAP. Subclasses should set auth_user_model and organization attributes.

    For verification against CU for instance, AccountRequestVerifyForm.organization should be 'ucb'
    and the AccountRequestVerifyForm.auth_user_model should be CuLdapUser.
    """
    username = forms.CharField(max_length=48,required=True)
    password = forms.CharField(max_length=255,widget=forms.PasswordInput,required=True)
    department = forms.CharField(max_length=128,required=True)
    role = forms.ChoiceField(choices=REQUEST_ROLES,required=True)

    @sensitive_variables('password')
    def clean(self):
        cleaned_data = super(AccountRequestVerifyForm,self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        account_requests = AccountRequest.objects.filter(username=username,organization=self.organization)
        if account_requests.count() > 0:
            raise forms.ValidationError(
                'An account request has already been submitted for {}'.format(username)
            )
        try:
            suffixed_username = get_suffixed_username(username,self.organization)
            rc_user = RcLdapUser.objects.get_user_from_suffixed_username(suffixed_username)
            rc_users = RcLdapUser.objects.filter(username=username)
            if rc_user:
                raise forms.ValidationError(
                    'An account already exists with username {}'.format(username)
                )

            authed = False
            auth_user = self.auth_user_model.objects.get(username=username)
            authed = auth_user.authenticate(password)
            if not authed:
                raise forms.ValidationError('Invalid password')
            return cleaned_data

        except UnboundLocalError:
            raise forms.ValidationError('Invalid organization')
        except self.auth_user_model.DoesNotExist:
            raise forms.ValidationError('Invalid username')
        except TypeError:
            raise forms.ValidationError('Missing field(s)')


class AccountRequestVerifyUcbForm(AccountRequestVerifyForm):
    organization = 'ucb'
    auth_user_model = CuLdapUser


class AccountRequestVerifyCsuForm(AccountRequestVerifyForm):
    organization = 'csu'
    auth_user_model = CsuLdapUser


class AccountRequestIntentForm(forms.Form):
    reason_summit = forms.BooleanField(required=False)
    reason_course = forms.BooleanField(required=False)
    reason_petalibrary = forms.BooleanField(required=False)
    reason_blanca = forms.BooleanField(required=False)

    # Summit additional info
    additional_summit_pi_email = forms.EmailField(required=False)
    additional_summit_funding = forms.CharField(widget=forms.Textarea,required=False)
    additional_summit_description = forms.CharField(widget=forms.Textarea,required=False)

    # Course follow-up
    additional_course_instructor_email = forms.EmailField(required=False)
    additional_course_number = forms.CharField(max_length=48,required=False)
