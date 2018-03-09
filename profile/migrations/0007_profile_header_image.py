# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0006_auto_20171004_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='header_image',
            field=models.ImageField(upload_to=b'user/%Y/%m', max_length=256, verbose_name='Header Image', blank=True),
        ),
    ]
