# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import lib.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allocation_id', models.SlugField(unique=True, null=True, blank=True)),
                ('amount', models.BigIntegerField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='AllocationRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abstract', models.TextField()),
                ('funding', models.TextField()),
                ('proposal', models.FileField(null=True, upload_to=b'proposals/%Y/%m/%d', blank=True)),
                ('time_requested', models.BigIntegerField()),
                ('amount_awarded', models.BigIntegerField(null=True, blank=True)),
                ('disk_space', models.IntegerField(default=0, null=True, blank=True)),
                ('software_request', models.TextField(null=True, blank=True)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'w', max_length=16, choices=[(b'a', b'Approved'), (b'd', b'Denied'), (b'w', b'Waiting'), (b'h', b'Hold'), (b'r', b'Ready For Review'), (b'q', b'Response Requested'), (b'i', b'Denied - Insufficient Resources'), (b'x', b'Denied - Proposal Incomplete'), (b'f', b'Approved - Fully Funded'), (b'p', b'Approved - Partially Funded')])),
                ('approved_on', models.DateTimeField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('allocation', models.ForeignKey(blank=True, to='projects.Allocation', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pi_emails', lib.fields.ListField()),
                ('organization', models.CharField(max_length=128, choices=[(b'ucb', b'University of Colorado Boulder'), (b'csu', b'Colorado State University'), (b'xsede', b'XSEDE')])),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('project_id', models.CharField(max_length=24, unique=True, null=True, blank=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('parent_account', models.CharField(max_length=24, null=True, blank=True)),
                ('qos_addenda', models.CharField(max_length=128, null=True, blank=True)),
                ('deactivated', models.BooleanField(default=False)),
                ('collaborators', models.ManyToManyField(related_name='collaborator_on', to=settings.AUTH_USER_MODEL)),
                ('managers', models.ManyToManyField(related_name='manager_on', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('link', models.TextField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='requester',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='allocation',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
        ),
    ]
