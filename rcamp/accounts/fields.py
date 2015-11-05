from django.db.models import fields
from ldapdb import escape_ldap_filter
import datetime


class DateTimeField(fields.DateTimeField):

    def from_ldap(self,value,connection):
        if len(value) == 0:
            return None
        else:
            v=value[0].decode(connection.charset)
            return datetime.datetime.strptime(v,"%Y%m%d%H%M%SZ")

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        "Returns field's value prepared for database lookup."
        if lookup_type in ['gt','gte','lt','lte','exact','iexact']:
            return ["%s" % escape_ldap_filter(value)]
        elif lookup_type in ['range','in'] :
            return [escape_ldap_filter(v) for v in value]

        raise TypeError("DateTimeField has invalid lookup: %s" % lookup_type)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ['gt','gte','lt','lte','exact','iexact']:
            return "%s" % escape_ldap_filter(value)
        elif lookup_type in ['range','in'] :
            return [escape_ldap_filter(v) for v in value]

        raise TypeError("DateTimeField has invalid lookup: %s" % lookup_type)


    def get_db_prep_save(self, value, connection):
        v=value.strftime("%Y%m%d%H%M%SZ")
        return [v.encode(connection.charset)]