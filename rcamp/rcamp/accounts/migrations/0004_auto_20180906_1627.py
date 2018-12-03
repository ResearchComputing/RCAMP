# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20180228_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=set([('username', 'organization', 'email')]),
        ),
    ]
