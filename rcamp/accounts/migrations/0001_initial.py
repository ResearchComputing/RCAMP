# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=12)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('login_shell', models.CharField(default=b'/bin/bash', max_length=24, choices=[(b'/bin/bash', b'bash'), (b'/bin/tcsh', b'tcsh')])),
                ('resources_requested', models.CharField(max_length=256, null=True, blank=True)),
                ('organization', models.CharField(max_length=128, choices=[(b'cu', b'University of Colorado Boulder'), (b'csu', b'Colorado State University'), (b'xsede', b'XSEDE'), (b'internal', b'Internal')])),
                ('role', models.CharField(default=b'student', max_length=24, choices=[(b'student', b'Student'), (b'postdoc', b'Post Doc'), (b'faculty', b'Faculty'), (b'staff', b'Staff')])),
                ('status', models.CharField(default=b'p', max_length=16, choices=[(b'p', b'Pending'), (b'a', b'Approved'), (b'd', b'Denied'), (b'i', b'Incomplete')])),
                ('approved_on', models.DateTimeField(null=True, blank=True)),
                ('notes', models.TextField(default=b'')),
                ('request_date', models.DateTimeField(auto_now_add=True)),
            ],
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
                ('uid', ldapdb.models.fields.IntegerField(unique=True, db_column=b'unixUID')),
                ('edu_affiliation', ldapdb.models.fields.ListField(db_column=b'eduPersonAffiliation')),
                ('edu_primary_affiliation', ldapdb.models.fields.CharField(max_length=200, db_column=b'eduPersonPrimaryAffiliation')),
                ('cu_primary_major', ldapdb.models.fields.CharField(max_length=200, db_column=b'cuEduPersonPrimaryMajor1')),
                ('cu_home_department', ldapdb.models.fields.CharField(max_length=200, db_column=b'cuEduPersonHomeDepartment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IdTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(unique=True, max_length=12)),
                ('min_id', models.IntegerField()),
                ('max_id', models.IntegerField()),
                ('next_id', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RcLdapGroup',
            fields=[
                ('dn', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'dn')),
                ('gid', ldapdb.models.fields.IntegerField(db_column=b'gidNumber')),
                ('name', ldapdb.models.fields.CharField(max_length=200, db_column=b'cn')),
                ('members', ldapdb.models.fields.ListField(null=True, db_column=b'memberUid', blank=True)),
            ],
            options={
                'abstract': False,
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
                ('uid', ldapdb.models.fields.IntegerField(db_column=b'uidNumber')),
                ('gid', ldapdb.models.fields.IntegerField(db_column=b'gidNumber')),
                ('gecos', ldapdb.models.fields.CharField(max_length=200, db_column=b'gecos')),
                ('home_directory', ldapdb.models.fields.CharField(max_length=200, db_column=b'homeDirectory')),
                ('login_shell', ldapdb.models.fields.CharField(default=b'/bin/bash', max_length=200, db_column=b'loginShell')),
                ('role', ldapdb.models.fields.ListField(null=True, db_column=b'curcRole', blank=True)),
                ('affiliation', ldapdb.models.fields.ListField(null=True, db_column=b'curcAffiliation', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
