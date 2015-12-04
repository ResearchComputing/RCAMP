# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20151204_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocation',
            name='members',
            field=projects.models.ListField(default=[], null=True, blank=True),
        ),
    ]
