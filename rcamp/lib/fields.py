from django.db import models
from django import forms
from django.core.validators import validate_email
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
        # elif isinstance(value, list):
        #     return value
        # else:
        #     return ast.literal_eval(value)
        else:
            return value.split(',')

    def get_prep_value(self, value):
        # return str(value)
        return ','.join(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

# Form fields
class CsvField(forms.Field):
    default_error_messages = {
        'not_list': _('Value must be a comma-separated list.'),
    }

    def to_python(self, value):
        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(',')

    def validate(self, value):
        super(CsvField, self).validate(value)
        if not isinstance(value,list):
            raise ValidationError(self.error_messages['not_a_list'], code='not_a_list')

class LdapCsvField(CsvField):
    # Circumvents unicode error in python-ldap
    def to_python(self, value):
        # Return an empty list if no input was given.
        if not value:
            return []
        return [str(v) for v in value.split(',')]

class MultiEmailField(forms.Field):
    def to_python(self, value):
        "Normalize data to a list of strings."

        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(',')

    def validate(self, value):
        "Check if value consists only of valid emails."

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)

        for email in value:
            validate_email(email)
