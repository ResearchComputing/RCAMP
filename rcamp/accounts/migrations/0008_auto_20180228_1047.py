# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20180228_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intent',
            name='account_request',
            field=models.OneToOneField(null=True, blank=True, to='accounts.AccountRequest'),
        ),
    ]
