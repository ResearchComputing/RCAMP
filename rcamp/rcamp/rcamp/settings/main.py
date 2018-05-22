import os
from .toggles import *

BASE_DIR = '/home/uwsgi/rcamp'


if not DEBUG:
    SECRET_KEY = os.environ.get('RCAMP_SECRET_KEY')
else:
    SECRET_KEY = 'A terribly insecure key not suitable for production'

if not DEBUG:
    default_hosts = 'rcamp.rc.colorado.edu,portals.rc.colorado.edu,rcamp1.rc.int.colorado.edu'
    hosts = os.environ.get('RCAMP_ALLOWEDHOSTS',default_hosts)
    ALLOWED_HOSTS = hosts.split(',')
else:
    ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
    'rest_framework',

    'ldapdb',
    'lib',
    'mailer',
    'accounts',
    'projects',
]

if DEBUG:
    INSTALLED_APPS.append('tests')

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'rcamp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,'rcamp','templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rcamp.wsgi.application'



LOGIN_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Denver'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'rcamp','static'),
)

# Media files (User-uploaded files)
# https://docs.djangoproject.com/en/1.8/ref/settings/#media-root
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media','')

# GRAPPELLI ADMIN SETTINGS
GRAPPELLI_ADMIN_TITLE = 'RCAMP'

REST_FRAMEWORK = {}
