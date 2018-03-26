# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20180326_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='time_requested',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
