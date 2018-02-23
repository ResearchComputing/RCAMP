# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20180223_1416'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountrequest',
            name='intent',
        ),
        migrations.AddField(
            model_name='intent',
            name='account_request',
            field=models.ForeignKey(default=1, to='accounts.AccountRequest'),
            preserve_default=False,
        ),
    ]
