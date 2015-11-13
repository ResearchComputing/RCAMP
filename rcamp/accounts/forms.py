from django import forms
from accounts.models import CuLdapUser


class CuAuthForm(forms.Form):
    username = forms.CharField(max_length=12,required=True)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super(CuAuthForm,self).clean()
        un = cleaned_data.get('username')
        pw = cleaned_data.get('password')
        try:
            user = CuLdapUser.objects.get(username=un)
            authed = user.authenticate(pw)
            if not authed:
                raise forms.ValidationError('Invalid password')
            return cleaned_data
        except CuLdapUser.DoesNotExist:
            raise forms.ValidationError('Invalid username')
