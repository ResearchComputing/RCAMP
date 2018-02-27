# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20180223_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intent',
            name='account_request',
            field=models.OneToOneField(to='accounts.AccountRequest'),
        ),
    ]