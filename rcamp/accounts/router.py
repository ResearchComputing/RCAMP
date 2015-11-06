def is_ldap_model(model):
    return hasattr(model, 'base_dn')

class LdapRouter(object):
    """
    A router to point database operations on LDAP models to the one
    of the LDAP databases.
    """

    def allow_migrate(self, db, model):
        if is_ldap_model(model):
            return False
        return None

    def db_for_read(self, model, **hints):
        "Point all operations on LDAP models to the appropriate LDAP database"
        if is_ldap_model(model):
            if model._meta.object_name.startswith('Cu'):
                return 'culdap'
            else:
                return 'rcldap'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on LDAP models to the appropriate LDAP database"
        if is_ldap_model(model):
            if model._meta.object_name.startswith('Cu'):
                return 'culdap'
            else:
                return 'rcldap'
        return None
