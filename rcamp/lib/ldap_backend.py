from django_auth_ldap.backend import LDAPBackend

class AUTH_CSU_LDAP_Backend(LDAPBackend):
    settings_prefix = "AUTH_CSU_LDAP_"

class AUTH_RC_LDAP_Backend(LDAPBackend):
    settings_prefix = "AUTH_RC_LDAP_"
