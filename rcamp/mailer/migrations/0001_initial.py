# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MailLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('from_host', models.CharField(max_length=256)),
                ('recipient_emails', models.CharField(max_length=1024)),
                ('reference_name', models.CharField(max_length=256)),
                ('email_object', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MailNotifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('event', models.CharField(max_length=128, choices=[(b'account_created_from_request', b'account_created_from_request'), (b'account_request_received', b'account_request_received'), (b'allocation_created_from_request', b'allocation_created_from_request'), (b'allocation_request_created_by_user', b'allocation_request_created_by_user'), (b'project_created_by_user', b'project_created_by_user')])),
                ('mailto', models.TextField(null=True, blank=True)),
                ('cc', models.TextField(null=True, blank=True)),
                ('bcc', models.TextField(null=True, blank=True)),
                ('from_address', models.EmailField(max_length=254, null=True, blank=True)),
                ('subject', models.CharField(max_length=256)),
                ('body', models.TextField()),
            ],
        ),
    ]
