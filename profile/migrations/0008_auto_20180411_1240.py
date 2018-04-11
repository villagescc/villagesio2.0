# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0007_profile_header_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='feed_radius',
            field=models.IntegerField(blank=True, null=True, choices=[(-1, b'Anywhere'), (1000, 'Within 1 km'), (5000, 'Within 5 km'), (10000, 'Within 10 km'), (50000, 'Within 50 km')]),
        ),
    ]
