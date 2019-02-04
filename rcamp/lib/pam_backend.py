from django.conf import settings
from accounts.models import (
    RcLdapUser,
    User
)
import pam



class PamBackend():
    def authenticate(self, username=None, password=None):
        rc_user = RcLdapUser.objects.get_user_from_suffixed_username(username)
        if not rc_user:
            return None

        p = pam.pam()
        authed = p.authenticate(username, password, service=settings.PAM_SERVICES['default'])

        if authed:
            user_dict = {
                'first_name': rc_user.first_name,
                'last_name': rc_user.last_name,
                'email': rc_user.email,
            }
            user, created = User.objects.update_or_create(
                username=username,
                defaults=user_dict
            )
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
