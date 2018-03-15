# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0011_listings_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='tag',
            field=models.ManyToManyField(to='tags.Tag', blank=True),
        ),
    ]
