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
                ('organization', models.CharField(max_length=128, choices=[(b'ucb', b'University of Colorado Boulder'), (b'csu', b'Colorado State University'), (b'xsede', b'XSEDE'), (b'internal', b'Internal')])),
                ('role', models.CharField(default=b'student', max_length=24, choices=[(b'student', b'Student'), (b'postdoc', b'Post Doc'), (b'faculty', b'Faculty'), (b'staff', b'Staff')])),
                ('status', models.CharField(default=b'p', max_length=16, choices=[(b'p', b'Pending'), (b'a', b'Approved'), (b'd', b'Denied'), (b'i', b'Incomplete')])),
                ('approved_on', models.DateTimeField(null=True, blank=True)),
                ('notes', models.TextField(default=b'')),
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
        ),
    ]
