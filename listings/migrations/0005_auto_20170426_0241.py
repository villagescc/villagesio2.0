# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0004_listings_subcategories'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='description',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='listings',
            name='listing_type',
            field=models.CharField(max_length=2, choices=[('OF', 'Offer'), ('RQ', 'Request'), ('TC', 'Teach'), ('LR', 'Learn'), ('GT', 'Gift')]),
        ),
        migrations.AlterField(
            model_name='listings',
            name='photo',
            field=models.ImageField(null=True, upload_to='listings', blank=True),
        ),
        migrations.AlterField(
            model_name='listings',
            name='price',
            field=models.DecimalField(max_digits=6, decimal_places=2),
        ),
    ]
