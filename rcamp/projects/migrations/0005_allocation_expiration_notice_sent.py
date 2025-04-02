# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20180326_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='expiration_notice_sent',
            field=models.BooleanField(default=False),
        ),
    ]
