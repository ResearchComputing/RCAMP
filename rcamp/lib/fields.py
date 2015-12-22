from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
import ast


# Model fields
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

# Form fields
class CsvField(forms.fields.CharField):
    default_error_messages = {
        'not_list': _('Value is not a List.'),
    }
    
    def __init__(self, *args, **kwargs):
        initial_val = kwargs.get('initial')
        if initial_val:
            initial_val = ','.join(initial)
        else:
            initial_val = ''
        kwargs.update({'initial':initial_val})
        super(CsvField,self).__init__(*args,**kwargs)
    
    def validate(self, value):
        super(CsvField, self).validate(value)
        if not isinstance(val,list):
            raise ValidationError(self.error_messages['not_a_list'], code='not_a_list')
    
    def to_python(self, value):
        if value in self.empty_values:
            return []
        value = value.strip()
        value = value.split(',')
        return value
