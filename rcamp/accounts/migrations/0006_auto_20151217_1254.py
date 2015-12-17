# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20151217_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='notes',
            field=models.TextField(default=b''),
        ),
    ]
