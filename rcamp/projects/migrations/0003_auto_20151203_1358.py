# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_project_created_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allocation_id', models.CharField(unique=True, max_length=24)),
                ('title', models.CharField(max_length=256)),
                ('award', models.BigIntegerField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('members', models.CharField(default=b'[]', max_length=2048)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.CharField(default=datetime.datetime(2015, 12, 3, 20, 58, 0, 539949, tzinfo=utc), max_length=12, choices=[(b'S', b'Startup'), (b'CLS', b'Class'), (b'CU', b'CU Project'), (b'XSEDE', b'XSEDE Project')]),
            preserve_default=False,
        ),
    ]
