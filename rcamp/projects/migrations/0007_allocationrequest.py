# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_allocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abstract', models.TextField()),
                ('funding', models.TextField()),
                ('proposal', models.FileField(upload_to=b'')),
                ('time_requested', models.BigIntegerField()),
                ('amount_awarded', models.BigIntegerField(default=0)),
                ('disk_space', models.IntegerField()),
                ('software_request', models.TextField(null=True, blank=True)),
                ('requester', models.CharField(max_length=12)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'w', max_length=16, choices=[(b'a', b'Approved'), (b'd', b'Denied'), (b'w', b'Waiting'), (b'h', b'Hold'), (b'r', b'Ready For Review'), (b'q', b'Response Requested'), (b'i', b'Denied - Insufficient Resources'), (b'x', b'Denied - Proposal Incomplete'), (b'f', b'Approved - Fully Funded'), (b'p', b'Approved - Partially Funded')])),
                ('approved_on', models.DateTimeField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
        ),
    ]
