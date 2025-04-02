# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailnotifier',
            name='event',
            field=models.CharField(max_length=128, choices=[(b'account_created_from_request', b'account_created_from_request'), (b'account_request_received', b'account_request_received'), (b'allocation_created_from_request', b'allocation_created_from_request'), (b'allocation_expired', b'allocation_expired'), (b'allocation_expiring', b'allocation_expiring'), (b'allocation_request_created_by_user', b'allocation_request_created_by_user'), (b'project_created_by_user', b'project_created_by_user')]),
        ),
    ]
