# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_auto_20170515_1840'),
        ('listings', '0008_auto_20170515_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taglisting',
            name='listing_id',
        ),
        migrations.RemoveField(
            model_name='taglisting',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='listings',
            name='tags',
        ),
        migrations.AddField(
            model_name='listings',
            name='tag',
            field=models.ManyToManyField(to='tags.Tag', null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='TagListing',
        ),
    ]
