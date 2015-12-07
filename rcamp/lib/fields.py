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
