from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Func, F
from django.db.models.functions import Substr, Lower
from django.utils import timezone
from lib import fields

from accounts.models import User
from mailer.signals import allocation_created_from_request

class Cast(Func):
    function = 'CAST'
    template = '%(function)s(%(expressions)s as %(target_type)s)'

class Project(models.Model):
    ORGANIZATIONS = (
        ('ucb','University of Colorado Boulder'),
        ('csu','Colorado State University'),
        ('xsede','XSEDE'),
        ('amc', 'AMC'),
    )

    pi_emails = fields.ListField()
    managers = models.ManyToManyField(User,related_name='manager_on')
    collaborators = models.ManyToManyField(User,related_name='collaborator_on')
    organization = models.CharField(max_length=128,choices=ORGANIZATIONS)
    title = models.CharField(max_length=256)
    description = models.TextField()

    project_id = models.CharField(max_length=24,unique=True,blank=True,null=True)
    created_on = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True,null=True)

    parent_account = models.CharField(max_length=24,null=True,blank=True)
    qos_addenda = models.CharField(max_length=128,null=True,blank=True)
    deactivated = models.BooleanField(default=False)

    def __str__(self):
        return self.project_id

    def save(self,*args,**kwargs):
        if (not self.project_id) or (self.project_id == ''):
            # Assign new id to project.
            org = self.organization
            prefix_offset = len(org) + 1

            projects = Project.objects.filter(
                project_id__startswith=org
            ).annotate(
                project_number_int=Cast(Substr('project_id', prefix_offset), target_type='UNSIGNED')
            ).order_by('-project_number_int')

            if projects.count() == 0:
                next_id = '{}{}'.format(org.lower(),'1')
            else:
                last_id = projects[0].project_id
                last_id = last_id.replace(org,'')
                next_id = int(last_id) + 1
                next_id = '{}{}'.format(org.lower(),str(next_id))
            self.project_id = next_id
        super(Project,self).save(*args,**kwargs)

class Reference(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField()
    link = models.TextField()
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return '{}_{}'.format((self.project.project_id,str(self.created_on)))

class AllocationManager(models.Manager):
    def create_allocation_from_request(self,**kwargs):
        project = kwargs.get('project')
        amount_awarded = kwargs.get('amount_awarded', None)

        if not project:
            raise TypeError('Missing required field: project')

        if amount_awarded == None:
            raise TypeError('Missing required field: amount_awarded')

        now = timezone.now()
        next_year = now + relativedelta(years=1)

        alloc_fields = {}
        alloc_fields['project'] = project
        alloc_fields['amount'] = amount_awarded
        alloc_fields['start_date'] = now
        alloc_fields['end_date'] = next_year

        alloc = self.create(**alloc_fields)
        return alloc

class Allocation(models.Model):
    objects = AllocationManager()

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    allocation_id = models.SlugField(unique=True,blank=True,null=True)
    amount = models.BigIntegerField()
    created_on = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    expiration_notice_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.allocation_id

    def save(self,*args,**kwargs):
        alloc_id_tpl = '{project_id}_summit{alloc_enum}'

        if (not self.allocation_id) or (self.allocation_id == ''):
            proj_id = self.project.project_id
            search_prefix = '{project_id}_summit'.format(project_id=proj_id)
            prefix_offset = len(proj_id) + 1
            allocs = Allocation.objects.filter(
                allocation_id__startswith=search_prefix
            ).annotate(
                alloc_number_int=Cast(Substr('allocation_id', prefix_offset), target_type='UNSIGNED')
            ).order_by('-alloc_number_int')

            if allocs.count() == 0:
                next_id = alloc_id_tpl.format(
                    project_id=proj_id.lower(),
                    alloc_enum='1'
                )
            else:
                last_id = allocs.order_by('-allocation_id')[0].allocation_id
                last_id = last_id.replace(proj_id+'_summit','')
                next_id = int(last_id) + 1
                next_id = alloc_id_tpl.format(
                    project_id=proj_id.lower(),
                    alloc_enum=str(next_id)
                )
            self.allocation_id = next_id
        super(Allocation,self).save(*args,**kwargs)

class AllocationRequest(models.Model):
    STATUSES = (
        ('a','Approved'),
        ('d','Denied'),
        ('w','Waiting'),
        ('h','Hold'),
        ('r','Ready For Review'),
        ('q','Response Requested'),
        ('i','Denied - Insufficient Resources'),
        ('x','Denied - Proposal Incomplete'),
        ('f','Approved - Fully Funded'),
        ('p','Approved - Partially Funded'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    allocation = models.ForeignKey(
            Allocation,
            null=True,
            blank=True,
            on_delete=models.CASCADE
            )

    abstract = models.TextField(null=True,blank=True)
    funding = models.TextField(null=True,blank=True)
    proposal = models.FileField(upload_to='proposals/%Y/%m/%d',null=True,blank=True)
    time_requested = models.BigIntegerField(null=True,blank=True)

    amount_awarded = models.BigIntegerField(default=0)
    disk_space = models.IntegerField(default=0,null=True,blank=True)
    software_request = models.TextField(null=True,blank=True)

    requester = models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=16,choices=STATUSES,default='w')
    approved_on = models.DateTimeField(null=True,blank=True)
    notes = models.TextField(null=True,blank=True)

    def __str__(self):
        return '{}_{}'.format(self.project.project_id,self.request_date)

    def save(self,*args,**kwargs):
        # Check for change in approval status
        if (self.status in ['a','f','p']) and (not self.approved_on):
            # Approval process
            # logger.info('Approving project request: '+self.__str__())
            alloc = Allocation.objects.create_allocation_from_request(
                project = self.project,
                amount_awarded = self.amount_awarded
            )
            self.amount_awarded = alloc.amount
            allocation_created_from_request.send(sender=alloc.__class__,allocation=alloc)
            self.approved_on=timezone.now()
            self.allocation = alloc

        super(AllocationRequest,self).save(*args,**kwargs)
