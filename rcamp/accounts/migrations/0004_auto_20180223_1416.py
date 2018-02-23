# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20180222_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='intent',
            field=models.ForeignKey(blank=True, to='accounts.Intent', null=True),
        ),
    ]
