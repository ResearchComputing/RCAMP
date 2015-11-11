# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_rcldapuser_radius_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='status',
            field=models.CharField(default=b'p', max_length=16, choices=[(b'p', b'Pending'), (b'a', b'Approved'), (b'd', b'Denied'), (b'i', b'Incomplete')]),
        ),
    ]
