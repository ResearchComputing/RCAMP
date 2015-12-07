from django.db import models
from lib import fields


# Create your models here.
class Project(models.Model):
    PROJ_TYPES = (
        ('S','Startup'),
        ('CLS','Class'),
        ('CU','CU Project'),
        ('XSEDE','XSEDE Project'),
    )
    project_type = models.CharField(max_length=12,choices=PROJ_TYPES)
    project_id = models.CharField(max_length=24,unique=True)
    principal_investigator = models.CharField(max_length=12)
    title = models.CharField(max_length=256)
    created_on = models.DateField(auto_now_add=True)
    notes = models.TextField()
    allocations = fields.ListField(default=[],blank=True,null=True)
    
    def __unicode__(self):
        return self.project_id

class Allocation(models.Model):
    allocation_id = models.CharField(max_length=24,unique=True)
    title = models.CharField(max_length=256)
    award = models.BigIntegerField()
    created_on = models.DateField(auto_now_add=True)
    members = fields.ListField(default=[],blank=True,null=True)
    
    def __unicode__(self):
        return self.allocation_id
