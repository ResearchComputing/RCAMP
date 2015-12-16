# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountrequest',
            name='resources_requested',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
