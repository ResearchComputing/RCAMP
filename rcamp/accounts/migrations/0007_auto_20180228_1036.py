# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20180223_1657'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intent',
            name='resources_requested',
        ),
        migrations.AddField(
            model_name='intent',
            name='reason_blanca',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intent',
            name='reason_course',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intent',
            name='reason_petalibrary',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intent',
            name='reason_summit',
            field=models.BooleanField(default=False),
        ),
    ]
