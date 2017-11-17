# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('accounts', '0009_auto_20171113_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='accountrequest',
            name='projects',
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='organization',
            field=models.CharField(max_length=128, choices=[(b'csu', b'Colorado State University'), (b'xsede', b'XSEDE'), (b'internal', b'Research Computing - Administrative'), (b'ucb', b'University of Colorado Boulder')]),
        ),
    ]
