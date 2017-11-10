import ldap
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap.set_option(ldap.OPT_X_KEEPALIVE_IDLE,30)
ldap.set_option(ldap.OPT_X_KEEPALIVE_PROBES,2)
ldap.set_option(ldap.OPT_X_KEEPALIVE_INTERVAL,2)

# MEDIA_URL = 'http://localhost:9000/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'rcamp.sqlite',
    },
    'rcldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://localhost:10389',
        'USER': 'cn=Directory Manager',
        'PASSWORD': 'password',
    },
    'culdap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://localhost:10389',
        'USER': 'cn=Directory Manager',
        'PASSWORD': 'password',
    },
    'csuldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://localhost:10389',
        'USER': 'cn=Directory Manager',
        'PASSWORD': 'password',
    },
}

LDAPCONFS = {
    'rcldap': {
        'server': DATABASES['rcldap']['NAME'],
        'bind_dn': DATABASES['rcldap']['USER'],
        'bind_pw': DATABASES['rcldap']['PASSWORD'],
        'base_dn': 'dc=rc,dc=int,dc=colorado,dc=edu',
        'people_dn': 'ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'ucb_dn': 'ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'csu_dn': 'ou=csu,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'xsede_dn': 'ou=xsede,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'internal_dn': 'ou=internal,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'group_dn': 'ou=groups,dc=rc,dc=int,dc=colorado,dc=edu',
    },
    'culdap': {
        'server': DATABASES['culdap']['NAME'],
        'bind_dn': DATABASES['culdap']['USER'],
        'bind_pw': DATABASES['culdap']['PASSWORD'],
        'base_dn': 'dc=colorado,dc=edu',
        'group_dn': 'ou=groups,dc=colorado,dc=edu',
        'people_dn': 'ou=users,dc=colorado,dc=edu',
    },
    'csuldap': {
        'server': DATABASES['csuldap']['NAME'],
        'bind_dn': DATABASES['csuldap']['USER'],
        'bind_pw': DATABASES['csuldap']['PASSWORD'],
        'base_dn': 'ou=eIdentityUsers,dc=ColoState,dc=edu',
        'group_dn': 'ou=eIdentityUsers,dc=ColoState,dc=edu',
        'people_dn': 'ou=eIdentityUsers,dc=ColoState,dc=edu',
    },
}

TIME_ZONE = 'America/Denver'

# DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
