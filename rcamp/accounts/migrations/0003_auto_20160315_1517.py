# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20160315_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountrequest',
            name='course_number',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='accountrequest',
            name='id_verified_by',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
