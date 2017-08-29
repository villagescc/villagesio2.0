# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0006_auto_20170429_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='listing_type',
            field=models.CharField(max_length=100, choices=[('OFFER', 'Offer'), ('REQUEST', 'Request'), ('TEACH', 'Teach'), ('LEARN', 'Learn'), ('GIFT', 'Gift')]),
        ),
    ]
