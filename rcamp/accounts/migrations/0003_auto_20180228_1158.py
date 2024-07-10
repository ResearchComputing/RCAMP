# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20171213_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='Intent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason_summit', models.BooleanField(default=False)),
                ('reason_course', models.BooleanField(default=False)),
                ('reason_petalibrary', models.BooleanField(default=False)),
                ('reason_blanca', models.BooleanField(default=False)),
                ('sponsor_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('course_instructor_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('course_number', models.CharField(max_length=128, null=True, blank=True)),
                ('summit_description', models.TextField(null=True, blank=True)),
                ('summit_funding', models.TextField(null=True, blank=True)),
                ('summit_pi_email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='accountrequest',
            name='department',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='organization',
            field=models.CharField(max_length=128, choices=[(b'csu', b'Colorado State University'), (b'xsede', b'XSEDE'), (b'amc', b'AMC'), (b'ncar', b'NCAR'), (b'ucb', b'University of Colorado Boulder'), (b'internal', b'Research Computing - Administrative')]),
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='role',
            field=models.CharField(default=b'undergraduate', max_length=24, choices=[(b'undergraduate', b'Undergraduate'), (b'graduate', b'Graduate'), (b'postdoc', b'Post Doc'), (b'instructor', b'Instructor'), (b'faculty', b'Faculty'), (b'affiliated_faculty', b'Affiliated Faculty'), (b'staff', b'Staff'), (b'sponsored', b'Sponsored Affiliate')]),
        ),
        migrations.AddField(
            model_name='intent',
            name='account_request',
            field=models.OneToOneField(null=True, blank=True, to='accounts.AccountRequest', on_delete=models.CASCADE),
        ),
    ]
