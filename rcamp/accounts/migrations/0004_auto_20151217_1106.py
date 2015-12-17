# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_accountrequest_login_shell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountrequest',
            name='login_shell',
            field=models.CharField(default=b'/bin/bash', max_length=24, choices=[(b'/bin/bash', b'bash'), (b'/bin/tcsh', b'tcsh')]),
        ),
    ]
