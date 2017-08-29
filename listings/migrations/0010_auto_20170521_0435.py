# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0009_auto_20170515_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='description',
            field=models.CharField(max_length=5000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='listings',
            name='listing_type',
            field=models.CharField(max_length=100, choices=[(b'OFFER', b'OFFER'), (b'REQUEST', b'REQUEST'), (b'TEACH', b'TEACH'), (b'LEARN', b'LEARN')]),
        ),
        migrations.AlterField(
            model_name='listings',
            name='price',
            field=models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='listings',
            name='tag',
            field=models.ManyToManyField(to='tags.Tag'),
        ),
        migrations.AlterField(
            model_name='listings',
            name='title',
            field=models.CharField(max_length=70),
        ),
    ]
