# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_auto_20180411_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='amount',
            field=account.models.AmountField(null=True, max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='memo',
            field=models.TextField(null=True, blank=True),
        ),
    ]
