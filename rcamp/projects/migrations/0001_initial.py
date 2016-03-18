# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import lib.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pi_emails', lib.fields.ListField()),
                ('managers', lib.fields.ListField()),
                ('collaborators', lib.fields.ListField()),
                ('organization', models.CharField(max_length=128, choices=[(b'ucb', b'University of Colorado Boulder'), (b'csu', b'Colorado State University'), (b'xsede', b'XSEDE')])),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('project_id', models.CharField(unique=True, max_length=24)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('notes', models.TextField()),
                ('qos_addenda', models.CharField(max_length=128, null=True, blank=True)),
                ('deactivated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('link', models.TextField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
        ),
    ]
