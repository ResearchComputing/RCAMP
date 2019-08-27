import os
from .toggles import *

if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('RCAMP_EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('RCAMP_EMAIL_PORT'))
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARN',
            'class': 'logging.FileHandler',
            'filename': '/opt/logs/rcamp.log',
        },
        'management_commands': {
            'level': "INFO",
            'class': 'logging.FileHandler',
            'filename': '/opt/logs/management_commands.log'
        }
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
        'management_commands': {
            'handlers': ['management_commands'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
