from django.db import models
import ldapdb.models.fields as ldap_fields
import datetime
import ldapdb.models
import logging


logger = logging.getLogger(__name__)


# Create your models here.
ORGANIZATIONS = (
    ('ucb','University of Colorado Boulder'),
    ('xsede','XSEDE'),
)

class AccountRequest(models.Model):
    STATUSES = (
        ('p','Pending'),
        ('a','Approved'),
        ('d','Denied'),
        ('i','Incomplete'),
    )
    
    username = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=128,blank=False,null=False)
    last_name = models.CharField(max_length=128,blank=False,null=False)
    email = models.EmailField(unique=True)

    organization = models.CharField(choices=ORGANIZATIONS,blank=False,null=False)

    status = models.BooleanField(choices=STATUSES,default='p')
    approved_on = models.DateTimeField(null=True,blank=True)
    notes = models.TextField()

    request_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def from_db(cls,db,field_names,values):
        instance = super(AccountRequest,cls).from_db(cls,db,field_names,values)
        # Store original field values on the instance
        instance._loaded_values = dict(zip(field_names,values))
        return instance
    
    def save(self,*args,**kwargs):
        # Check for change in approval status
        if (self.status == 'a') and (self._loaded_values['status'] != 'a'):
            # Approval process
            logger.info('Approving account request: '+self.username)
            self.approved_on=datetime.datetime.now()
            RcLdapUser.objects.create_user_from_request(
                username=self.username,
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                organization=self.organization
            )
        
        super(AccountRequest,self).save(*args,**kwargs)

class LdapUser(ldapdb.models.Model):
    # inetOrgPerson
    first_name = ldap_fields.CharField(db_column='givenName')
    last_name = ldap_fields.CharField(db_column='sn')
    full_name = ldap_fields.CharField(db_column='cn')
    email = ldap_fields.CharField(db_column='mail')
    # posixAccount
    username = ldap_fields.CharField(db_column='uid', primary_key=True)
    # ldap specific
    modified_date = ldap_fields.DateTimeField(db_column='modifytimestamp',blank=True)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name

    class Meta:
        abstract=True

class RcLdapUserManager(models.Manager):
    def create_user_from_request(self,username,**kwargs):
        try:
            username = kwargs.get('username')
            first_name = kwargs.get('first_name')
            last_name = kwargs.get('last_name')
            email = kwargs.get('email')
            organization = kwargs.get('organization')
        except KeyError:
            logger.error('No all required values supplied to user create.')
            raise FieldError
            
        user_fields = {}
        user_fields['first_name'] = first_name.strip()
        user_fields['last_name'] = last_name.strip()
        user_fields['full_name'] = '%s, %s' % (user_fields['first_name'],user_fields['last_name'])
        user_fields['email'] = email.strip()
        user_fields['username'] = username.strip()
        # UID,GID handling currently missing,
        # as well as handling for auth domains
        user_fields['gecos'] = "%s %s,,," % (user_fields['first_name'],user_fields['last_name'])
        user_fields['home_directory'] = '/home/%s' % user_fields['username']
        user = self.create(**user_fields)
        return user

class RcLdapUser(LdapUser):
    objects = RcLdapUserManager()
    
    base_dn = settings.LDAPCONFS['rcldap']['people_dn']
    object_classes = ['top','person','inetorgperson','posixaccount','curcradiususer']
    uid = ldap_fields.IntegerField(db_column='uidNumber', unique=True)
    gid = ldap_fields.IntegerField(db_column='gidNumber')
    gecos =  ldap_fields.CharField(db_column='gecos')
    home_directory = ldap_fields.CharField(db_column='homeDirectory')
    login_shell = ldap_fields.CharField(db_column='loginShell', default='/bin/bash')
    radius_name = ldap_fields.CharField(db_column='curcradiusname')

    def active(self):
        return 'deactivated-' not in self.radius_name

class CuLdapUser(LdapUser):
    base_dn = settings.LDAPCONFS['culdap']['people_dn']
    object_classes = None
    uid = ldap_fields.IntegerField(db_column='unixUID', unique=True)
    # Used for automatic determination of role and affiliation.
    edu_affiliation = ldap_fields.ListField(db_column='eduPersonAffiliation')
    edu_primary_affiliation = ldap_fields.CharField(db_column='eduPersonPrimaryAffiliation')
    cu_primary_major = ldap_fields.CharField(db_column='cuEduPersonPrimaryMajor1')
    cu_home_department = ldap_fields.CharField(db_column='cuEduPersonHomeDepartment')

class RcLdapGroup(ldapdb.models.Model):
    base_dn =  settings.LDAPCONFS['rcldap']['group_dn']
    object_classes = ['top','posixGroup']
    # posixGroup attributes
    gid = ldap_fields.IntegerField(db_column='gidNumber', unique=True)
    name = ldap_fields.CharField(db_column='cn', max_length=200, primary_key=True)
    members = ldap_fields.ListField(db_column='memberUid')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
