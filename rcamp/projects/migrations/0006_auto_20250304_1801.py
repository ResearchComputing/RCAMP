# Generated by Django 2.2.28 on 2025-03-05 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_allocation_expiration_notice_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='proposal',
            field=models.FileField(blank=True, null=True, upload_to='proposals/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='status',
            field=models.CharField(choices=[('a', 'Approved'), ('d', 'Denied'), ('w', 'Waiting'), ('h', 'Hold'), ('r', 'Ready For Review'), ('q', 'Response Requested'), ('i', 'Denied - Insufficient Resources'), ('x', 'Denied - Proposal Incomplete'), ('f', 'Approved - Fully Funded'), ('p', 'Approved - Partially Funded')], default='w', max_length=16),
        ),
        migrations.AlterField(
            model_name='project',
            name='organization',
            field=models.CharField(choices=[('ucb', 'University of Colorado Boulder'), ('csu', 'Colorado State University'), ('xsede', 'XSEDE'), ('amc', 'AMC')], max_length=128),
        ),
    ]
