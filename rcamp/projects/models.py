from django.db import models
import ast


class ListField(models.TextField):
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return []
        else:
            return ast.literal_eval(value)
    
    def to_python(self, value):
        if not value:
            return []
        elif isinstance(value, list):
            return value
        else:
            return ast.literal_eval(value)
    
    def get_prep_value(self, value):
        return str(value)
    
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

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
    allocations = ListField(default=[],blank=True,null=True)
    
    def __unicode__(self):
        return self.project_id

class Allocation(models.Model):
    allocation_id = models.CharField(max_length=24,unique=True)
    title = models.CharField(max_length=256)
    award = models.BigIntegerField()
    created_on = models.DateField(auto_now_add=True)
    members = ListField(default=[],blank=True,null=True)
    
    def __unicode__(self):
        return self.allocation_id
