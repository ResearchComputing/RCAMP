from django.conf import settings
from django.contrib.auth.models import User
from accounts.models import RcLdapUser
import pam



class PamBackend():
    def authenticate(self, username=None, password=None):
        try:
            rc_user = RcLdapUser.objects.get(username=username)
        except RcLdapUser.DoesNotExist:
            return None

        p = pam.pam()
        authed = p.authenticate(username,password,service='login')

        if authed:
            user_dict = {
                'first_name': rc_user.first_name,
                'last_name': rc_user.last_name,
                'email': rc_user.email,
                'is_staff': False,
            }
            user, created = User.objects.update_or_create(
                username=rc_user.username,
                defaults=user_dict
            )
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
