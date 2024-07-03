# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone
import django.core.validators
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
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
                'managed': False,
                'verbose_name_plural': 'LDAP users',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AccountRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=48)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('sponsor_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('course_number', models.CharField(max_length=128, null=True, blank=True)),
                ('login_shell', models.CharField(default=b'/bin/bash', max_length=24, choices=[(b'/bin/bash', b'bash'), (b'/bin/tcsh', b'tcsh')])),
                ('resources_requested', models.CharField(max_length=256, null=True, blank=True)),
                ('organization', models.CharField(max_length=128, choices=[(b'csu', b'Colorado State University'), (b'xsede', b'XSEDE'), (b'amc', b'AMC'), (b'internal', b'Research Computing - Administrative'), (b'ucb', b'University of Colorado Boulder')])),
                ('role', models.CharField(default=b'student', max_length=24, choices=[(b'student', b'Student'), (b'postdoc', b'Post Doc'), (b'faculty', b'Faculty'), (b'staff', b'Staff'), (b'sponsored', b'Sponsored Affiliate')])),
                ('status', models.CharField(default=b'p', max_length=16, choices=[(b'p', b'Pending'), (b'a', b'Approved'), (b'd', b'Denied'), (b'i', b'Incomplete')])),
                ('approved_on', models.DateTimeField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('id_verified_by', models.CharField(max_length=128, null=True, blank=True)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
            ],
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
            options={
                'verbose_name': 'ID tracker',
                'verbose_name_plural': 'ID trackers',
            },
        ),
    ]
