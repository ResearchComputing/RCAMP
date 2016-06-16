# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_allocationrequest_allocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='parent_account',
            field=models.CharField(max_length=24, null=True, blank=True),
        ),
    ]
