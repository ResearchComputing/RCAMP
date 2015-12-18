# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151217_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsuUser',
            fields=[
                ('rcldapuser_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='accounts.RcLdapUser')),
            ],
            options={
                'abstract': False,
            },
            bases=('accounts.rcldapuser',),
        ),
        migrations.CreateModel(
            name='CuUser',
            fields=[
                ('rcldapuser_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='accounts.RcLdapUser')),
            ],
            options={
                'abstract': False,
            },
            bases=('accounts.rcldapuser',),
        ),
        migrations.CreateModel(
            name='InternalUser',
            fields=[
                ('rcldapuser_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='accounts.RcLdapUser')),
            ],
            options={
                'abstract': False,
            },
            bases=('accounts.rcldapuser',),
        ),
        migrations.CreateModel(
            name='XsedeUser',
            fields=[
                ('rcldapuser_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='accounts.RcLdapUser')),
            ],
            options={
                'abstract': False,
            },
            bases=('accounts.rcldapuser',),
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='organization',
            field=models.CharField(max_length=128, choices=[(b'cu', b'University of Colorado Boulder'), (b'csu', b'Colorado State University'), (b'xsede', b'XSEDE'), (b'internal', b'Internal')]),
        ),
    ]
