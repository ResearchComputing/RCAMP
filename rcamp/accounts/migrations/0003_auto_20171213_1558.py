# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20171213_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='username',
            field=models.CharField(max_length=48),
        ),
    ]
