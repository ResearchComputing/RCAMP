# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_allocationrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocationrequest',
            name='allocation',
            field=models.ForeignKey(blank=True, to='projects.Allocation', null=True),
        ),
    ]
