# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_on',
            field=models.DateField(default=datetime.datetime(2015, 12, 3, 20, 18, 53, 936151, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
