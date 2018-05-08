from .toggles import *

if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mail.rc.int.colorado.edu'
    EMAIL_PORT = 25
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'WARN',
                'class': 'logging.FileHandler',
                'filename': 'rcamp.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'rcamp': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'projects': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'accounts': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
