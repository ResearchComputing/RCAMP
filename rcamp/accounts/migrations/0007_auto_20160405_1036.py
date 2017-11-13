# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_accountrequest_projects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
