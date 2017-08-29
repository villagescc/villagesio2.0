# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0003_auto_20170516_1436'),
        ('profile', '0004_profile_job'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='tag',
            field=models.ManyToManyField(to='tags.Tag', null=True, blank=True),
        ),
    ]
