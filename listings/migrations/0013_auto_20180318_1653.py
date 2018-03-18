# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0012_auto_20180315_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='price',
            field=models.DecimalField(default=Decimal('0'), max_digits=6, decimal_places=2),
        ),
    ]
