# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='abstract',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='funding',
            field=models.TextField(null=True, blank=True),
        ),
    ]
