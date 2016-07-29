# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_project_parent_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='disk_space',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='proposal',
            field=models.FileField(null=True, upload_to=b'proposals/%Y/%m/%d', blank=True),
        ),
    ]
