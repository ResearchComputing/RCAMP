# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20160729_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='amount_awarded',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
