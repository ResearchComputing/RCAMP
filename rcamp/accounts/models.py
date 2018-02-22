from django.db import models
from django.conf import settings
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth.models import AbstractUser
from lib import ldap_utils
import ldapdb.models.fields as ldap_fields
import ldapdb.models
import logging
import datetime
import pam

from mailer.signals import account_created_from_request

logger = logging.getLogger(__name__)


# Create your models here.
ORGANIZATIONS = tuple([(k,v['long_name']) for k,v in settings.ORGANIZATION_INFO.iteritems()])

REQUEST_ROLES = (
    ('undergraduate','Undergraduate',),
    ('graduate','Graduate',),
    ('postdoc','Post Doc',),
    ('instructor','Instructor',),
    ('faculty','Faculty',),
    ('affiliated_faculty','Affiliated Faculty',),
    ('staff','Staff',),
    ('sponsored','Sponsored Affiliate',),
)

ROLES = REQUEST_ROLES + (
    ('pi','Principal Investigator',),
    ('admin','Admin',),
)

SHELL_CHOICES = (
    ('/bin/bash','bash'),
    ('/bin/tcsh','tcsh'),
)

class User(AbstractUser):
    @property
    def organization(self):
        _, organization = ldap_utils.get_ldap_username_and_org(self.username)
        return organization

    @property
    def ldap_username(self):
        ldap_username, _ = ldap_utils.get_ldap_username_and_org(self.username)
        return ldap_username

    def get_ldap_user(self):
        """Return the RcLdapUser associated with this account."""
        ldap_user = RcLdapUser.objects.get_user_from_suffixed_username(self.username)
        return ldap_user


class AccountRequest(models.Model):
    class Meta:
        unique_together = (('username','organization'),)

    STATUSES = (
        ('p','Pending'),
        ('a','Approved'),
        ('d','Denied'),
        ('i','Incomplete'),
    )

    username = models.CharField(max_length=48)
    first_name = models.CharField(max_length=128,blank=False,null=False)
    last_name = models.CharField(max_length=128,blank=False,null=False)
    email = models.EmailField(unique=True)

    organization = models.CharField(max_length=128,choices=ORGANIZATIONS,blank=False,null=False)
    department = models.CharField(max_length=128,blank=True,null=True)
    role = models.CharField(max_length=24,choices=REQUEST_ROLES,default='undergraduate')

    status = models.CharField(max_length=16,choices=STATUSES,default='p')
    approved_on = models.DateTimeField(null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    id_verified_by = models.CharField(max_length=128,blank=True,null=True)

    intent = models.ForeignKey('Intent',null=True)

    request_date = models.DateTimeField(auto_now_add=True)

    # TODO: Deprecate these fields, as they are now represented in the Intent object
    login_shell = models.CharField(max_length=24,choices=SHELL_CHOICES,default='/bin/bash')
    resources_requested = models.CharField(max_length=256,blank=True,null=True)
    sponsor_email = models.EmailField(blank=True,null=True)
    course_number = models.CharField(max_length=128,blank=True,null=True)

    def __unicode__(self):
        return '%s_%s'%(self.username,self.request_date)

    def save(self,*args,**kwargs):
        # Has model already been approved?
        if (self.status == 'a') and (not self.approved_on):
            # Approval process
            logger.info('Approving account request: '+self.username)
            self.approved_on=timezone.now()
            rc_user = RcLdapUser.objects.create_user_from_request(
                username=self.username,
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                organization=self.organization,
                role=self.role
            )
            account_created_from_request.send(sender=rc_user.__class__,account=rc_user)
        super(AccountRequest,self).save(*args,**kwargs)

class Intent(models.Model):
    resources_requested = models.TextField(blank=True,null=True)
    sponsor_email = models.EmailField(blank=True,null=True)
    course_instructor_email = models.EmailField(blank=True,null=True)
    course_number = models.CharField(max_length=128,blank=True,null=True)
    summit_description = models.TextField(null=True,blank=True)
    summit_funding = models.TextField(null=True,blank=True)
    summit_pi_email = models.EmailField(blank=True,null=True)

class IdTracker(models.Model):
    class Meta:
        verbose_name = 'ID tracker'
        verbose_name_plural = 'ID trackers'

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
    class Meta:
        managed = False

    rdn_key = 'username'

    # inetOrgPerson
    first_name = ldap_fields.CharField(db_column='givenName')
    last_name = ldap_fields.CharField(db_column='sn')
    full_name = ldap_fields.CharField(db_column='cn')
    email = ldap_fields.CharField(db_column='mail')
    # posixAccount
    username = ldap_fields.CharField(db_column='uid')
    # ldap specific
    modified_date = ldap_fields.DateTimeField(db_column='modifytimestamp',blank=True)

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
    def get_user_from_suffixed_username(self,suffixed_username):
        username, organization = ldap_utils.get_ldap_username_and_org(suffixed_username)
        users = [u for u in self.get_queryset().filter(username=username) if u.organization == organization]
        user = None
        if len(users) > 0:
            user = users[0]
        return user

    def create(self,*args,**kwargs):
        org = kwargs.pop('organization', None)
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True,using=self.db,organization=org)
        return obj

    def create_user_from_request(self,**kwargs):
        username = kwargs.get('username')
        if username is not None:
            username = str(username).strip()
            username = username.lower()
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        email = kwargs.get('email')
        if email is not None:
            email = str(email).strip()
        organization = kwargs.get('organization')
        if not all([username,first_name,last_name,email,organization]):
            raise TypeError('Missing required field.')

        id_tracker = IdTracker.objects.get(category='posix')
        if organization == 'ucb':
            cu_user = CuLdapUser.objects.get(username=username)
            uid = cu_user.uid
        else:
            uid = id_tracker.get_next_id()
        user_fields = {}
        user_fields['first_name'] = first_name.strip()
        user_fields['last_name'] = last_name.strip()
        user_fields['full_name'] = '%s, %s' % (user_fields['last_name'],user_fields['first_name'])
        user_fields['email'] = email
        user_fields['username'] = username
        user_fields['uid'] = uid
        user_fields['gid'] = uid
        user_fields['gecos'] = "%s %s,,," % (user_fields['first_name'],user_fields['last_name'])
        suffixed_username = ldap_utils.get_suffixed_username(user_fields['username'],organization)
        user_fields['home_directory'] = '/home/%s' % suffixed_username
        user_fields['organization'] = organization

        role = kwargs.get('role')
        role = str(role)
        if role:
            if role == 'sponsored':
                today = datetime.date.today()
                expiration_date = today.replace(year=today.year+1)
                user_fields['expires'] = date_to_sp_expire(expiration_date)
            if role in ['faculty','affiliated_faculty']:
                user_fields['role'] = ['pi',role]
            else:
                user_fields['role'] = [role]

        user = self.create(**user_fields)
        pgrp = RcLdapGroup.objects.create(
                name='%spgrp'%username,
                gid=user_fields['gid'],
                members=[username],
                organization=organization
            )
        sgrp_gid = id_tracker.get_next_id()
        sgrp = RcLdapGroup.objects.create(
                name='%sgrp'%username,
                gid=sgrp_gid,
                members=[username],
                organization=organization
            )

        # Add CU users to ucb posix group
        if ('ucb' in settings.LICENSE_GROUPS) and (organization == 'ucb'):
            license_grp = settings.LICENSE_GROUPS['ucb']
            ucb_grps = RcLdapGroup.objects.filter(name=license_grp)
            if ucb_grps.count() > 0:
                ucb_grp = ucb_grps[0]
                # TODO: Extend ldapdb ListField to include an append method.
                ucb_grp.members = ucb_grp.members + [username]
                ucb_grp.save(organization='ucb')

        return user

class RcLdapUser(LdapUser):
    class Meta:
        verbose_name = 'LDAP user'
        verbose_name_plural = 'LDAP users'
        managed = False

    def __init__(self,*args,**kwargs):
        super(RcLdapUser,self).__init__(*args,**kwargs)
        rdn = self.dn.lower().replace(self.base_dn.lower(), '')
        rdn_list = rdn.split(',')
        self.org = ''
        if len(rdn_list) > 2:
            ou = rdn_list[-2]
            __, org = ou.split('=')
            self.org = org
            self.base_dn = ','.join([ou,self.base_dn])

    objects = RcLdapUserManager()

    base_dn = settings.LDAPCONFS['rcldap']['people_dn']
    object_classes = ['top','person','inetorgperson','posixaccount','curcPerson','shadowAccount']
    expires = ldap_fields.IntegerField(db_column='shadowExpire',blank=True,null=True)
    uid = ldap_fields.IntegerField(db_column='uidNumber',null=True,blank=True)
    gid = ldap_fields.IntegerField(db_column='gidNumber',null=True,blank=True)
    gecos = ldap_fields.CharField(db_column='gecos',default='')
    home_directory = ldap_fields.CharField(db_column='homeDirectory')
    login_shell = ldap_fields.CharField(db_column='loginShell', default='/bin/bash')
    #curcPerson attributes
    role = ldap_fields.ListField(db_column='curcRole',blank=True,null=True)
    affiliation = ldap_fields.ListField(db_column='curcAffiliation',blank=True,null=True)

    @property
    def organization(self):
        return self.org

    @property
    def effective_uid(self):
        suffixed_username = ldap_utils.get_suffixed_username(self.username,self.organization)
        return suffixed_username

    def _set_base_dn(self,org):
        if org in settings.ORGANIZATION_INFO.keys():
            ou = 'ou={}'.format(org)
            self.org = org
            if ou not in self.base_dn.lower():
                self.base_dn = ','.join([ou,self.base_dn])
        else:
            raise ValueError('Invalid organization specified: {}'.format(org))

    def save(self,*args,**kwargs):
        org = kwargs.pop('organization', None)
        if not org:
            raise ValueError('No organization specified.')
        self._set_base_dn(org)

        # If no UID/GID specified, auto-assign
        if (self.uid == None) and (self.gid == None):
            id_tracker = IdTracker.objects.get(category='posix')
            uid = id_tracker.get_next_id()
            self.uid = uid
            self.gid = uid
        elif self.uid == None:
            self.uid = self.gid
        elif self.gid == None:
            self.gid = self.uid

        super(RcLdapUser,self).save(*args,**kwargs)

class CuLdapUser(LdapUser):
    class Meta:
        managed = False

    base_dn = settings.LDAPCONFS['culdap']['people_dn']
    object_classes = []
    uid = ldap_fields.IntegerField(db_column='uidNumber', unique=True)
    # Used for automatic determination of role and affiliation.
    edu_affiliation = ldap_fields.ListField(db_column='eduPersonAffiliation')
    edu_primary_affiliation = ldap_fields.CharField(db_column='eduPersonPrimaryAffiliation')
    cu_primary_major = ldap_fields.CharField(db_column='cuEduPersonPrimaryMajor1')
    cu_home_department = ldap_fields.CharField(db_column='cuEduPersonHomeDepartment')

    @sensitive_variables('pwd')
    def authenticate(self,pwd):
        authed = ldap_utils.authenticate(self.dn,pwd,'culdap')
        return authed

class CsuLdapUser(LdapUser):
    class Meta:
        managed = False

    base_dn = settings.LDAPCONFS['csuldap']['people_dn']
    object_classes = []

    @sensitive_variables('pwd')
    def authenticate(self,pwd):
        p = pam.pam()
        authed = p.authenticate(self.username, pwd, service=settings.PAM_SERVICES['csu'])
        return authed
# Monkey-patch LDAP attr names in field bindings
CsuLdapUser._meta.get_field('username').db_column = 'sAMAccountName'
CsuLdapUser._meta.get_field('username').column = 'sAMAccountName'

class RcLdapGroupManager(models.Manager):
    def create(self,*args,**kwargs):
        org = kwargs.pop('organization', None)
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True,using=self.db,organization=org)
        return obj

class RcLdapGroup(ldapdb.models.Model):
    class Meta:
        verbose_name = 'LDAP group'
        verbose_name_plural = 'LDAP groups'
        managed = False

    def __init__(self,*args,**kwargs):
        super(RcLdapGroup,self).__init__(*args,**kwargs)
        rdn = self.dn.lower().replace(self.base_dn.lower(), '')
        rdn_list = rdn.split(',')
        self.org = ''
        if len(rdn_list) > 2:
            ou = rdn_list[-2]
            __, org = ou.split('=')
            self.org = org
            self.base_dn = ','.join([ou,self.base_dn])

    objects = RcLdapGroupManager()

    rdn_key = 'name'
    base_dn =  settings.LDAPCONFS['rcldap']['group_dn']
    object_classes = ['top','posixGroup']
    # posixGroup attributes
    # gid = ldap_fields.IntegerField(db_column='gidNumber', unique=True)
    gid = ldap_fields.IntegerField(db_column='gidNumber',null=True,blank=True)
    name = ldap_fields.CharField(db_column='cn', max_length=200)
    members = ldap_fields.ListField(db_column='memberUid',blank=True,null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    @property
    def organization(self):
        return self.org

    @property
    def effective_cn(self):
        suffixed_name = ldap_utils.get_suffixed_username(self.name,self.organization)
        return suffixed_name

    def _set_base_dn(self,org):
        if org in settings.ORGANIZATION_INFO.keys():
            ou = 'ou={}'.format(org)
            self.org = org
            if ou not in self.base_dn.lower():
                self.base_dn = ','.join([ou,self.base_dn])
        else:
            raise ValueError('Invalid organization specified: {}'.format(org))

    def save(self,*args,**kwargs):
        org = kwargs.pop('organization', None)
        if not org:
            raise ValueError('No organization specified.')
        self._set_base_dn(org)
        force_insert = kwargs.pop('force_insert',None)

        # If no GID specified, auto-assign
        if self.gid == None:
            id_tracker = IdTracker.objects.get(category='posix')
            gid = id_tracker.get_next_id()
            self.gid = gid

        super(RcLdapGroup,self).save(*args,**kwargs)


def date_to_sp_expire (date_, epoch=datetime.date(year=1970, day=1, month=1)):
    return (date_ - epoch).days
