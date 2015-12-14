from django import forms
from accounts.models import CuLdapUser
from accounts.models import RcLdapUser
from accounts.models import AccountRequest


class CuAuthForm(forms.Form):
    username = forms.CharField(max_length=12,required=True)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super(CuAuthForm,self).clean()
        un = cleaned_data.get('username')
        pw = cleaned_data.get('password')
        if AccountRequest.objects.filter(username=un).count() > 0:
            raise forms.ValidationError(
                'An account request has already been submitted for {}'.format(un)
            )
        try:
            if RcLdapUser.objects.filter(username=un).count() > 0:
                raise forms.ValidationError(
                    'An account already exists with username {}'.format(un)
                )
            user = CuLdapUser.objects.get(username=un)
            authed = user.authenticate(pw)
            if not authed:
                raise forms.ValidationError('Invalid password')
            return cleaned_data
        except CuLdapUser.DoesNotExist:
            raise forms.ValidationError('Invalid username')
        except TypeError:
            raise forms.ValidationError('Missing field(s)')
