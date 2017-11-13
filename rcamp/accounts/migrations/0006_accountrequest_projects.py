# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20160322_1244'),
        ('accounts', '0003_auto_20160315_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountrequest',
            name='projects',
            field=models.ManyToManyField(to='projects.Project', blank=True),
        ),
    ]
