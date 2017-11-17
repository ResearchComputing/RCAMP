# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20171117_1026'),
        ('projects', '0012_auto_20160928_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='requester',
            field=models.ForeignKey(blank=True, to='accounts.PortalUser', null=True),
        ),
        migrations.RemoveField(
            model_name='project',
            name='collaborators',
        ),
        migrations.AddField(
            model_name='project',
            name='collaborators',
            field=models.ManyToManyField(related_name='collaborator_on', to='accounts.PortalUser'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='managers',
        ),
        migrations.AddField(
            model_name='project',
            name='managers',
            field=models.ManyToManyField(related_name='manager_on', to='accounts.PortalUser'),
        ),
    ]
