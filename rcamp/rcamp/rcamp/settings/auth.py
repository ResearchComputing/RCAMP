AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lib.pam_backend.PamBackend',
)

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/login'

PAM_SERVICES = {
    'default': 'login',
    'csu': 'csu'
}
