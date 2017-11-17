# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0012_auto_20160928_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='requester',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.RemoveField(
            model_name='project',
            name='collaborators',
        ),
        migrations.AddField(
            model_name='project',
            name='collaborators',
            field=models.ManyToManyField(related_name='collaborator_on', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='project',
            name='managers',
        ),
        migrations.AddField(
            model_name='project',
            name='managers',
            field=models.ManyToManyField(related_name='manager_on', to=settings.AUTH_USER_MODEL),
        ),
    ]
