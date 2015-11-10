from django.db import models
from django.conf import settings
from django.views.decorators.debug import sensitive_variables
from accounts.ldap_utils import LdapObject
from accounts.fields import DateTimeField
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

    organization = models.CharField(max_length=128,choices=ORGANIZATIONS,blank=False,null=False)

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

class IdTracker(models.Model):
    category = models.CharField(max_length=12,blank=False,null=False,unique=True)
    min_id = models.IntegerField(blank=False,null=False)
    max_id = models.IntegerField(blank=False,null=False)
    next_id = models.IntegerField(blank=True,null=True)

    def __unicode__(self):
        return self.category

    def get_next_id(self):
        if self.next_id:
            uid = self.next_id
        else:
            uid = self.min_id
        while uid < self.max_id:
            rc_users = RcLdapUser.objects.filter(uid=uid)
            rc_groups = RcLdapGroup.objects.filter(gid=uid)

            if all([(len(rc_users)==0),(len(rc_groups)==0)]):
                self.next_id = uid + 1
                self.save()
                return uid
            else:
                uid += 1

class LdapUser(ldapdb.models.Model):
    # inetOrgPerson
    first_name = ldap_fields.CharField(db_column='givenName')
    last_name = ldap_fields.CharField(db_column='sn')
    full_name = ldap_fields.CharField(db_column='cn')
    email = ldap_fields.CharField(db_column='mail')
    # posixAccount
    username = ldap_fields.CharField(db_column='uid', primary_key=True)
    # ldap specific
    modified_date = DateTimeField(db_column='modifytimestamp',blank=True)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name

    def save(self,*args,**kwargs):
        force_insert = kwargs.pop('force_insert',None)
        super(LdapUser,self).save(*args,**kwargs)

    class Meta:
        abstract=True

class RcLdapUserManager(models.Manager):
    def create_user_from_request(self,**kwargs):
        try:
            username = kwargs.get('username')
            first_name = kwargs.get('first_name')
            last_name = kwargs.get('last_name')
            email = kwargs.get('email')
            organization = kwargs.get('organization')
        except KeyError:
            logger.error('No all required values supplied to user create.')
            raise FieldError
        
        id_tracker = IdTracker.objects.get(category='posix')
        uid = id_tracker.get_next_id()
        user_fields = {}
        user_fields['first_name'] = first_name.strip()
        user_fields['last_name'] = last_name.strip()
        user_fields['full_name'] = '%s, %s' % (user_fields['last_name'],user_fields['first_name'])
        user_fields['email'] = email.strip()
        user_fields['username'] = username.strip()
        user_fields['uid'] = uid
        user_fields['gid'] = uid
        user_fields['gecos'] = "%s %s,,," % (user_fields['first_name'],user_fields['last_name'])
        user_fields['home_directory'] = '/home/%s' % user_fields['username']
        user = self.create(**user_fields)
        pgrp = RcLdapGroup.objects.create(
                name='%spgrp'%username,
                gid=user_fields['gid'],
                members=[username]
            )
        sgrp_gid = id_tracker.get_next_id()
        sgrp = RcLdapGroup.objects.create(
                name='%sgrp'%username,
                gid=sgrp_gid,
                members=[username]
            )
        return user

class RcLdapUser(LdapUser):
    objects = RcLdapUserManager()
    
    base_dn = settings.LDAPCONFS['rcldap']['people_dn']
    object_classes = ['top','person','inetorgperson','posixaccount']
    uid = ldap_fields.IntegerField(db_column='uidNumber', unique=True)
    gid = ldap_fields.IntegerField(db_column='gidNumber')
    gecos =  ldap_fields.CharField(db_column='gecos')
    home_directory = ldap_fields.CharField(db_column='homeDirectory')
    login_shell = ldap_fields.CharField(db_column='loginShell', default='/bin/bash')

    # def active(self):
    #     return 'deactivated-' not in self.radius_name

class CuLdapUser(LdapUser):
    base_dn = settings.LDAPCONFS['culdap']['people_dn']
    object_classes = None
    uid = ldap_fields.IntegerField(db_column='unixUID', unique=True)
    # Used for automatic determination of role and affiliation.
    edu_affiliation = ldap_fields.ListField(db_column='eduPersonAffiliation')
    edu_primary_affiliation = ldap_fields.CharField(db_column='eduPersonPrimaryAffiliation')
    cu_primary_major = ldap_fields.CharField(db_column='cuEduPersonPrimaryMajor1')
    cu_home_department = ldap_fields.CharField(db_column='cuEduPersonHomeDepartment')
    
    @sensitive_variables('pwd')
    def authenticate(self,pwd):
        l=LdapObject(**settings.LDAPCONFS['culdap'])
        br=l.authenticate(self.username,pwd)
        if br:
            return True
        else:
            return False

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
    
    def save(self,*args,**kwargs):
        force_insert = kwargs.pop('force_insert',None)
        super(RcLdapGroup,self).save(*args,**kwargs)
