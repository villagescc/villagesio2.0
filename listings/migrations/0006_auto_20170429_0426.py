# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0005_auto_20170426_0241'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='listings',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
