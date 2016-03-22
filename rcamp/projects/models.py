from django.db import models
from lib import fields


# Create your models here.
# class Allocation(models.Model):
#     allocation_id = models.CharField(max_length=24,unique=True)
#     title = models.CharField(max_length=256)
#     cpu_mins_awarded = models.FloatField()
#     created_on = models.DateField(auto_now_add=True)
#     members = fields.ListField(default=[],blank=True,null=True)
#
#     def __unicode__(self):
#         return self.allocation_id

class Project(models.Model):
    ORGANIZATIONS = (
        ('ucb','University of Colorado Boulder'),
        ('csu','Colorado State University'),
        ('xsede','XSEDE'),
    )

    pi_emails = fields.ListField()
    managers = fields.ListField()
    collaborators = fields.ListField()
    organization = models.CharField(max_length=128,choices=ORGANIZATIONS)
    title = models.CharField(max_length=256)
    description = models.TextField()

    project_id = models.CharField(max_length=24,unique=True,blank=True,null=True)
    # is_startup = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True,null=True)

    qos_addenda = models.CharField(max_length=128,null=True,blank=True)
    deactivated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.project_id

    def save(self,*args,**kwargs):
        if (not self.project_id) or (self.project_id == ''):
            # Assign new id to project.
            org = self.organization
            projects = Project.objects.filter(
                    project_id__startswith=org
                ).order_by(
                    '-project_id'
                )
            if projects.count() == 0:
                next_id = '{}{}'.format(org.lower(),'1')
            else:
                last_id = projects[0].project_id
                last_id = last_id.replace(org,'')
                next_id = int(last_id) + 1
                next_id = '{}{}'.format(org.lower(),str(next_id))
            self.project_id = next_id
        super(Project,self).save(*args,**kwargs)

    # @property
    # def current_limit(self):
    #     allocs = self.allocations.all()
    #     limit = 0.0
    #     for a in allocs:
    #         limit += a.cpu_mins_awarded
    #     return limit

class Reference(models.Model):
    project = models.ForeignKey(Project)
    description = models.TextField()
    link = models.TextField()
    created_on = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return '{}_{}'.format((self.project.project_id,str(self.created_on)))

# class AllocationRequest(models.Model):
#     STATUSES = (
#         ('a','Approved'),
#         ('d','Denied'),
#         ('w','Waiting'),
#         ('h','Hold'),
#         ('r','Ready For Review'),
#         ('q','Response Requested'),
#         ('i','Denied - Insufficient Resources'),
#         ('x','Denied - Proposal Incomplete'),
#         ('f','Approved - Fully Funded'),
#         ('p','Approved - Partially Funded'),
#     )
#
#     title = models.CharField(max_length=256,unique=True)
#     abstract = models.TextField()
#     funding = models.TextField()
#     proposal = models.FileField()
#     time_requested = models.BigIntegerField()
#     cpu_mins_awarded = models.BigIntegerField(default=0)
#     disk_space = models.IntegerField()
#     software_request = models.TextField(null=True,blank=True)
#     members = fields.ListField(default=[],blank=True,null=True)
#
#     status = models.CharField(max_length=16,choices=STATUSES,default='w')
#     approved_on = models.DateTimeField(null=True,blank=True)
#     notes = models.TextField()
#     project = models.ForeignKey(Project)
#
#     requester = models.CharField(max_length=12)
#     request_date = models.DateTimeField(auto_now_add=True)
#
#     def __unicode__(self):
#         return '%s_%s'%(self.principal_investigator,self.request_date)
#
#     @classmethod
#     def from_db(cls,db,field_names,values):
#         instance = super(AllocationRequest,cls).from_db(db,field_names,values)
#         # Store original field values on the instance
#         instance._loaded_values = dict(zip(field_names,values))
#         return instance
#
#     def save(self,*args,**kwargs):
#         # Check for change in approval status
#         if (self.status in ['a','f','p']) and (self._loaded_values['status'] not in ['a','f','p']):
#             # Approval process
#             logger.info('Approving project request: '+self.__unicode__())
#             self.approved_on=timezone.now()
#
#         super(AllocationRequest,self).save(*args,**kwargs)
