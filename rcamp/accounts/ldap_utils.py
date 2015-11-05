from django.conf import settings
import ldap
import logging

logger = logging.getLogger(__name__)


def ldapentry_to_dict(result):
    r={}
    for key in result:
        r[key]=result[key][0]
    return r

def escape_ldap_filter(value):
    value = unicode(value)
    return value.replace('\\', '\\5c') \
                .replace('*', '\\2a') \
                .replace('(', '\\28') \
                .replace(')', '\\29') \
                .replace('\0', '\\00')

class LdapObject():
    def __init__(self,*args, **kwargs):
        self.priv_required=kwargs.get('priv_required',False)
        self.server = kwargs['server']
        self.base_dn = kwargs['base_dn']
        self.bind_dn = kwargs.get('bind_dn', '')
        self.bind_pw = kwargs.get('bind_pw', '')
        self.userfilter = kwargs.get('userfilter', 'uid=%s')
        self.groupfilter = kwargs.get('groupfilter','cn=%s')

        self.people_rdn = kwargs.get('people_rdn','ou=people')
        self.group_rdn = kwargs.get('group_rdn','ou=groups')
        self.people_dn="%s,%s"%(self.people_rdn,self.base_dn)
        self.group_dn="%s,%s"%(self.group_rdn,self.base_dn)

        logger.info('Trying to connect to %s' % self.server)
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        self.conn = ldap.initialize(self.server)


        if not self.conn:
            logger.error('Could not initialize connection to %s' % self.server)
            return

        if self.priv_required:
            self.bind_priv()

    def bind_priv(self):
        logger.debug('privledged bind called')

        return self.bind(self.bind_dn,self.bind_pw)

    def bind(self, dn='', pword=''):

        logger.info('bind called as:%s'%dn)

        try:
            self.conn.simple_bind_s(dn, pword)

        except ldap.INVALID_CREDENTIALS:
            logger.error('%s returned invalid credentials for %s' % (self.server, dn))
            return None

        except ldap.LDAPError, e:
            logger.error('Got error from LDAP library: %s' % str(e))

            return None

        logger.info('bind sucessful')
        return True

    def authenticate(self, username=None, password=None):
        if username is None or password is None or not username:
            logger.info('Authenticate: Username or password is None, automatically returning None')
            return None


        if self.priv_required:
            logger.debug('Authenticate: Trying a privledge bind')
            br=self.bind_priv()
        else:
            logger.debug('Authenticate: Trying an anonymous bind')
            br=self.bind()

        if br:
            logger.debug('Authenticate: Trying to search for users dn')
            (dn,entry) = self.find_person(username)
            if not dn:
                logger.debug('Authenticate: did not find dn returning False')
                return False
            br = self.bind(dn, password)
            if br:
                logger.info('Authenticate: Authenticated successfully as %s' % dn)

                authed= True
            else:
                logger.info('Authenticate: Authentication failed as %s' % dn)
                authed= False

            #switch context back to privleged user if need be
            if self.priv_required:self.bind_priv()
            return authed
        else:
            return None

    def find_person(self, username):
        """
        This function, with 'ou=people', will return a single (dn, LDAPEntry object) tuple or None if user not found
        using the configuration settings regarding users defined in the initialization.
        """
        logger.debug('find_person: using %s,%s,%s' % (self.people_dn, ldap.SCOPE_SUBTREE, self.userfilter % username))
        results = self.conn.search_s(self.people_dn, ldap.SCOPE_SUBTREE, self.userfilter % username,attrsonly=0)

        if len(results) == 0:
            logger.info("Did not find %s in ldap" % username)
            return (None,None)

        dn = results[0][0]
        ldapentry= ldapentry_to_dict(result=results[0][1])

        return (dn,ldapentry)

    def find_user(self, username):
        """
        This function, with 'ou=user', will return a single (dn, LDAPEntry object) tuple or None if user not found
        using the configuration settings regarding users defined in the initialization.
        """
        attrs = ['*']

        logger.debug('find_user: using %s,%s,%s,%s' % (self.user_dn, ldap.SCOPE_SUBTREE, self.userfilter % username, attrs))
        results = self.conn.search_s(self.user_dn, ldap.SCOPE_SUBTREE, self.userfilter % username, attrs)

        if len(results) == 0:
            logger.info("Did not find %s in ldap" % username)
            return (None,None)

        dn = results[0][0]
        ldapentry= ldapentry_to_dict(result=results[0][1])

        return (dn,ldapentry)