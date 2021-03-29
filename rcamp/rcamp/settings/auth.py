import os

AUTH_RC_LDAP_URI = os.getenv('RCAMP_RC_LDAP_URI')
AUTH_RC_LDAP_USER_DN_TEMPLATE = os.getenv('RCAMP_RC_LDAP_USER_DN_TEMPLATE')

AUTH_CSU_LDAP_URI = os.getenv('RCAMP_CSU_LDAP_URI')
AUTH_CSU_LDAP_USER_DN_TEMPLATE = os.getenv('RCAMP_CSU_LDAP_USER_DN_TEMPLATE')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lib.ldap_backend.AUTH_RC_LDAP_Backend',
    'lib.ldap_backend.AUTH_CSU_LDAP_Backend',
    'lib.pam_backend.PamBackend',
)

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/login'

PAM_SERVICES = {
    'default': 'login',
    'csu': 'csu'
}
