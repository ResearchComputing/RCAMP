# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20160315_1517'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='rcldapuser',
        #     name='expires',
        #     field=ldapdb.models.fields.DateTimeField(null=True, db_column=b'shadowExpire', blank=True),
        # ),
    ]
