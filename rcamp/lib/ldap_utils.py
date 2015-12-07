from django.conf import settings
from ldapdb import escape_ldap_filter
import ldap


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
