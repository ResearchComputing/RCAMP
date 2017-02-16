# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160405_1036'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='CsuLdapUser',
        #     fields=[
        #         ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
        #         ('first_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'givenName')),
        #         ('last_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'sn')),
        #         ('full_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
        #         ('email', ldapdb.models.fields.CharField(max_length=200, db_column=b'mail')),
        #         ('username', ldapdb.models.fields.CharField(max_length=200, db_column=b'sAMAccountName')),
        #         ('modified_date', ldapdb.models.fields.DateTimeField(db_column=b'modifytimestamp', blank=True)),
        #     ],
        #     options={
        #         'abstract': False,
        #     },
        # ),
        # migrations.CreateModel(
        #     name='CuLdapUser',
        #     fields=[
        #         ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
        #         ('first_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'givenName')),
        #         ('last_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'sn')),
        #         ('full_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
        #         ('email', ldapdb.models.fields.CharField(max_length=200, db_column=b'mail')),
        #         ('username', ldapdb.models.fields.CharField(max_length=200, db_column=b'uid')),
        #         ('modified_date', ldapdb.models.fields.DateTimeField(db_column=b'modifytimestamp', blank=True)),
        #         ('uid', ldapdb.models.fields.IntegerField(unique=True, db_column=b'unixUID')),
        #         ('edu_affiliation', ldapdb.models.fields.ListField(db_column=b'eduPersonAffiliation')),
        #         ('edu_primary_affiliation', ldapdb.models.fields.CharField(max_length=200, db_column=b'eduPersonPrimaryAffiliation')),
        #         ('cu_primary_major', ldapdb.models.fields.CharField(max_length=200, db_column=b'cuEduPersonPrimaryMajor1')),
        #         ('cu_home_department', ldapdb.models.fields.CharField(max_length=200, db_column=b'cuEduPersonHomeDepartment')),
        #     ],
        #     options={
        #         'abstract': False,
        #     },
        # ),
        # migrations.CreateModel(
        #     name='RcLdapGroup',
        #     fields=[
        #         ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
        #         ('gid', ldapdb.models.fields.IntegerField(db_column=b'gidNumber')),
        #         ('name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
        #         ('members', ldapdb.models.fields.ListField(null=True, db_column=b'memberUid', blank=True)),
        #     ],
        #     options={
        #         'verbose_name': 'LDAP group',
        #         'verbose_name_plural': 'LDAP groups',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='RcLdapUser',
        #     fields=[
        #         ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
        #         ('first_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'givenName')),
        #         ('last_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'sn')),
        #         ('full_name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
        #         ('email', ldapdb.models.fields.CharField(max_length=200, db_column=b'mail')),
        #         ('username', ldapdb.models.fields.CharField(max_length=200, db_column=b'uid')),
        #         ('modified_date', ldapdb.models.fields.DateTimeField(db_column=b'modifytimestamp', blank=True)),
        #         ('expires', ldapdb.models.fields.IntegerField(null=True, db_column=b'shadowExpire', blank=True)),
        #         ('uid', ldapdb.models.fields.IntegerField(db_column=b'uidNumber')),
        #         ('gid', ldapdb.models.fields.IntegerField(db_column=b'gidNumber')),
        #         ('gecos', ldapdb.models.fields.CharField(default=b'', max_length=200, db_column=b'gecos')),
        #         ('home_directory', ldapdb.models.fields.CharField(max_length=200, db_column=b'homeDirectory')),
        #         ('login_shell', ldapdb.models.fields.CharField(default=b'/bin/bash', max_length=200, db_column=b'loginShell')),
        #         ('role', ldapdb.models.fields.ListField(null=True, db_column=b'curcRole', blank=True)),
        #         ('affiliation', ldapdb.models.fields.ListField(null=True, db_column=b'curcAffiliation', blank=True)),
        #     ],
        #     options={
        #         'verbose_name': 'LDAP user',
        #         'verbose_name_plural': 'LDAP users',
        #     },
        # ),
        migrations.AlterModelOptions(
            name='idtracker',
            options={'verbose_name': 'ID tracker', 'verbose_name_plural': 'ID trackers'},
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='username',
            field=models.CharField(unique=True, max_length=48),
        ),
    ]