import os
from .toggles import *

BASE_DIR = '/opt/rcamp'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rcamp1712',
        'USER': os.environ.get('RCAMP_DB_USER'),
        'PASSWORD': os.environ.get('RCAMP_DB_PASSWORD'),
        'HOST': os.environ.get('RCAMP_DB_HOST'),
    },
    'rcldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': unicode(os.environ.get('RCAMP_RC_LDAP_URI')),
        'USER': unicode(os.environ.get('RCAMP_RC_LDAP_USER')),
        'PASSWORD': unicode(os.environ.get('RCAMP_RC_LDAP_PASSWORD')),
    },
    'culdap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': unicode(os.environ.get('RCAMP_UCB_LDAP_URI')),
        'USER': unicode(os.environ.get('RCAMP_UCB_LDAP_USER')),
        'PASSWORD': unicode(os.environ.get('RCAMP_UCB_LDAP_PASSWORD')),
    },
    'csuldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': unicode(os.environ.get('RCAMP_CSU_LDAP_URI')),
        'USER': unicode(os.environ.get('RCAMP_CSU_LDAP_USER')),
        'PASSWORD': unicode(os.environ.get('RCAMP_CSU_LDAP_PASSWORD')),
    },
}

LDAPCONFS = {
    'rcldap': {
        'server': unicode(DATABASES['rcldap']['NAME']),
        'bind_dn': unicode(DATABASES['rcldap']['USER']),
        'bind_pw': unicode(DATABASES['rcldap']['PASSWORD']),
        'base_dn': u'dc=rc,dc=int,dc=colorado,dc=edu',
        'people_dn': u'ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'ucb_dn': u'ou=ucb,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'csu_dn': u'ou=csu,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'xsede_dn': u'ou=xsede,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'internal_dn': u'ou=internal,ou=people,dc=rc,dc=int,dc=colorado,dc=edu',
        'group_dn': u'ou=groups,dc=rc,dc=int,dc=colorado,dc=edu',
    },
    'culdap': {
        'server': unicode(DATABASES['culdap']['NAME']),
        'bind_dn': unicode(DATABASES['culdap']['USER']),
        'bind_pw': unicode(DATABASES['culdap']['PASSWORD']),
        'base_dn': u'dc=colorado,dc=edu',
        'group_dn': u'ou=groups,dc=colorado,dc=edu',
        'people_dn': u'ou=users,dc=colorado,dc=edu',
    },
    'csuldap': {
        'server': unicode(DATABASES['csuldap']['NAME']),
        'bind_dn': unicode(DATABASES['csuldap']['USER']),
        'bind_pw': unicode(DATABASES['csuldap']['PASSWORD']),
        'base_dn': u'ou=eIdentityUsers,dc=ColoState,dc=edu',
        'group_dn': u'ou=eIdentityUsers,dc=ColoState,dc=edu',
        'people_dn': u'ou=eIdentityUsers,dc=ColoState,dc=edu',
    },
}

DATABASE_ROUTERS = ['lib.router.LdapRouter',]
