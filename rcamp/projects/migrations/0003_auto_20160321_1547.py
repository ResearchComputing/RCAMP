# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20160321_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
