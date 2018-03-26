# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20180326_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='amount_awarded',
            field=models.BigIntegerField(default=0),
        ),
    ]
