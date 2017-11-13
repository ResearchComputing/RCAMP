# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160405_1036'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='idtracker',
            options={'verbose_name': 'ID tracker', 'verbose_name_plural': 'ID trackers'},
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='username',
            field=models.CharField(unique=True, max_length=48),
        ),
    ]
