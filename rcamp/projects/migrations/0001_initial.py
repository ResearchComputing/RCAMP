# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import lib.fields


class Migration(migrations.Migration):

    dependencies = [
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
                ('members', lib.fields.ListField(default=[], null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_type', models.CharField(max_length=12, choices=[(b'S', b'Startup'), (b'CLS', b'Class'), (b'CU', b'CU Project'), (b'XSEDE', b'XSEDE Project')])),
                ('project_id', models.CharField(unique=True, max_length=24)),
                ('principal_investigator', models.CharField(max_length=12)),
                ('title', models.CharField(max_length=256)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('notes', models.TextField()),
                ('allocations', lib.fields.ListField(default=[], null=True, blank=True)),
            ],
        ),
    ]
