from django.conf import settings
from ldapdb import escape_ldap_filter
import ldap


def authenticate(dn,pwd,ldap_conf_key):
    # Setup connection
    ldap_conf = settings.LDAPCONFS[ldap_conf_key]
    server = ldap_conf['server']
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
    conn = ldap.initialize(server, bytes_mode=False)
    # Authenticate
    try:
        conn.simple_bind_s(dn, pwd)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False

def get_suffixed_username(username,organization):
    try:
        suffix = settings.ORGANIZATION_INFO[organization]['suffix']
    except KeyError:
        suffix = None
    suffixed_username = username
    if suffix:
        suffixed_username = '{0}@{1}'.format(username,suffix)
    return suffixed_username

def get_ldap_username_and_org(suffixed_username):
    username = suffixed_username
    org = 'ucb'
    if '@' in suffixed_username:
        username, suffix = suffixed_username.rsplit('@',1)
        for k,v in settings.ORGANIZATION_INFO.items():
            if v['suffix'] == suffix:
                org = k
                break
    return username, org
