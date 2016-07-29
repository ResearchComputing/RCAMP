# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_auto_20160729_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='disk_space',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='requester',
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
    ]
