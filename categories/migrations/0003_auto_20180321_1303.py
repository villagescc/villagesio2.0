# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_categories_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='icon',
            field=models.ImageField(null=True, upload_to='categories', blank=True),
        ),
    ]
