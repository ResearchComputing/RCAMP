# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20151203_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='allocations',
            field=projects.models.ListField(default=[], null=True, blank=True),
        ),
    ]
