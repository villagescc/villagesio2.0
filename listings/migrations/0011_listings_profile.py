# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0006_auto_20171004_1934'),
        ('listings', '0010_auto_20170521_0435'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='profile',
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to='profile.Profile', null=True),
        ),
    ]
