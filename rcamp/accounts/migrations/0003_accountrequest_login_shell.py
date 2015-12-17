# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_accountrequest_resources_requested'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountrequest',
            name='login_shell',
            field=models.CharField(default='/bin/bash', max_length=24),
            preserve_default=False,
        ),
    ]
