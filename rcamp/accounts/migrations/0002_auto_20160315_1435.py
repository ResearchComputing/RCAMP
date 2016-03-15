# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountrequest',
            name='sponsor_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='role',
            field=models.CharField(default=b'student', max_length=24, choices=[(b'student', b'Student'), (b'postdoc', b'Post Doc'), (b'faculty', b'Faculty'), (b'staff', b'Staff'), (b'sponsored', b'Sponsored Affiliate')]),
        ),
    ]
