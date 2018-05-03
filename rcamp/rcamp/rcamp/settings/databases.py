import os
from .toggles import *

BASE_DIR = '/opt/rcamp'

if not DEBUG:
    # TODO: Sort out a concise approach for loading these values
    DATABASES = {}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'rcamp.sqlite',
        },
        # `test-ldap` is the name of the researchcomputing/rc-test-ldap service
        'rcldap': {
            'ENGINE': 'ldapdb.backends.ldap',
            'NAME': 'ldap://test-ldap',
            'USER': 'cn=Directory Manager',
            'PASSWORD': 'password',
        },
        'culdap': {
            'ENGINE': 'ldapdb.backends.ldap',
            'NAME': 'ldap://test-ldap',
            'USER': 'cn=Directory Manager',
            'PASSWORD': 'password',
        },
        'csuldap': {
            'ENGINE': 'ldapdb.backends.ldap',
            'NAME': 'ldap://test-ldap',
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

DATABASE_ROUTERS = ['lib.router.LdapRouter',]
