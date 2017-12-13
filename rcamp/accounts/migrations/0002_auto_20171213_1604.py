# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='username',
            field=models.CharField(max_length=48),
        ),
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=set([('username', 'organization')]),
        ),
    ]
