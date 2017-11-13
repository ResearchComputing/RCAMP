# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('accounts', '0008_auto_20170105_1130'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsuLdapUser',
            fields=[
                ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
                ('first_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'givenName')),
                ('last_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'sn')),
                ('full_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
                ('email', ldapdb.models.fields.CharField(max_length=200, db_column=b'mail')),
                ('username', ldapdb.models.fields.CharField(max_length=200, db_column=b'sAMAccountName')),
                ('modified_date', ldapdb.models.fields.DateTimeField(db_column=b'modifytimestamp', blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CuLdapUser',
            fields=[
                ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
                ('first_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'givenName')),
                ('last_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'sn')),
                ('full_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
                ('email', ldapdb.models.fields.CharField(max_length=200, db_column=b'mail')),
                ('username', ldapdb.models.fields.CharField(max_length=200, db_column=b'uid')),
                ('modified_date', ldapdb.models.fields.DateTimeField(db_column=b'modifytimestamp', blank=True)),
                ('uid', ldapdb.models.fields.IntegerField(unique=True, db_column=b'uidNumber')),
                ('edu_affiliation', ldapdb.models.fields.ListField(db_column=b'eduPersonAffiliation')),
                ('edu_primary_affiliation', ldapdb.models.fields.CharField(max_length=200, db_column=b'eduPersonPrimaryAffiliation')),
                ('cu_primary_major', ldapdb.models.fields.CharField(max_length=200, db_column=b'cuEduPersonPrimaryMajor1')),
                ('cu_home_department', ldapdb.models.fields.CharField(max_length=200, db_column=b'cuEduPersonHomeDepartment')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RcLdapGroup',
            fields=[
                ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
                ('gid', ldapdb.models.fields.IntegerField(null=True, db_column=b'gidNumber', blank=True)),
                ('name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
                ('members', ldapdb.models.fields.ListField(null=True, db_column=b'memberUid', blank=True)),
            ],
            options={
                'verbose_name': 'LDAP group',
                'managed': False,
                'verbose_name_plural': 'LDAP groups',
            },
        ),
        migrations.CreateModel(
            name='RcLdapUser',
            fields=[
                ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
                ('first_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'givenName')),
                ('last_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'sn')),
                ('full_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
                ('email', ldapdb.models.fields.CharField(max_length=200, db_column=b'mail')),
                ('username', ldapdb.models.fields.CharField(max_length=200, db_column=b'uid')),
                ('modified_date', ldapdb.models.fields.DateTimeField(db_column=b'modifytimestamp', blank=True)),
                ('expires', ldapdb.models.fields.IntegerField(null=True, db_column=b'shadowExpire', blank=True)),
                ('uid', ldapdb.models.fields.IntegerField(null=True, db_column=b'uidNumber', blank=True)),
                ('gid', ldapdb.models.fields.IntegerField(null=True, db_column=b'gidNumber', blank=True)),
                ('gecos', ldapdb.models.fields.CharField(default=b'', max_length=200, db_column=b'gecos')),
                ('home_directory', ldapdb.models.fields.CharField(max_length=200, db_column=b'homeDirectory')),
                ('login_shell', ldapdb.models.fields.CharField(default=b'/bin/bash', max_length=200, db_column=b'loginShell')),
                ('role', ldapdb.models.fields.ListField(null=True, db_column=b'curcRole', blank=True)),
                ('affiliation', ldapdb.models.fields.ListField(null=True, db_column=b'curcAffiliation', blank=True)),
            ],
            options={
                'verbose_name': 'LDAP user',
                'verbose_name_plural': 'LDAP users',
                'managed': False,
            },
        ),
    ]
