from django.conf import settings
from ldapdb import escape_ldap_filter
import ldap


ORGANIZATION_INFO = {
    'ucb': {
        'long_name': 'University of Colorado Boulder'
        'suffix': None
    },
    'csu': {
        'long_name': 'Colorado State University'
        'suffix': 'colostate.edu'
    },
    'xsede': {
        'long_name': 'XSEDE'
        'suffix': 'xsede.org'
    },
    'internal': {
        'long_name': 'Research Computing - Administrative'
        'suffix': None
    }
}

def authenticate(dn,pwd,ldap_conf_key):
    # Setup connection
    ldap_conf = settings.LDAPCONFS[ldap_conf_key]
    server = ldap_conf['server']
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
    conn = ldap.initialize(server)
    # Authenticate
    try:
        conn.simple_bind_s(dn, pwd)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False

def get_suffixed_username(username,organization):
    suffix = ORGANIZATION_INFO[organization]['suffix']
    return '{0}@{1}'.format(username,suffix)

def get_ldap_username_and_org(suffixed_username):
    username = suffixed_username
    org = 'ucb'
    if '@' in suffixed_username:
        username, suffix = suffixed_username.split('@')
        for k,v in ORGANIZATION_INFO.iteritems():
            if v['suffix'] == suffix:
                org = k
                break
    return username, org
