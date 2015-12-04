# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_id', models.CharField(unique=True, max_length=24)),
                ('principal_investigator', models.CharField(max_length=12)),
                ('title', models.CharField(max_length=256)),
                ('notes', models.TextField()),
                ('allocations', models.CharField(default=b'[]', max_length=1024)),
            ],
        ),
    ]
