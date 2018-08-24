from .toggles import *

if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mail.rc.int.colorado.edu'
    EMAIL_PORT = 25
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

_log_level = 'DEBUG' if DEBUG else 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'rcamp': {
            'handlers': ['console'],
            'level': _log_level,
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console'],
            'level': _log_level,
            'propagate': True,
        },
        'projects': {
            'handlers': ['console'],
            'level': _log_level,
            'propagate': True,
        },
        'mailer': {
            'handlers': ['console'],
            'level': _log_level,
            'propagate': True,
        },
    },
}
