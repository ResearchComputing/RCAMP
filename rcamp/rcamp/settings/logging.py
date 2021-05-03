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
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'management_commands': {
            'level': "INFO",
            'class': 'logging.FileHandler',
            'filename': '/opt/logs/management_commands.log',
            'formatter': 'verbose'
        },
        'admin': {
            'level': "INFO",
            'class': 'logging.FileHandler',
            'filename': '/opt/logs/admin.log',
            'formatter': 'verbose'
        }
    },
    'formatters': {
        'verbose': {
            'format': 'RCAMP: {module} {levelname} {asctime}: {message}',
            'style': '{',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rcamp': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'projects': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'management_commands': {
            'handlers': ['management_commands', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'admin': {
            'handlers': ['admin', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['admin', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
