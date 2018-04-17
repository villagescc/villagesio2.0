# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20171004_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(max_length=50, choices=[(b'TRUST', b'Trust'), (b'PAYMENT', b'Payment')]),
        ),
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.CharField(default=b'NEW', max_length=16, choices=[(b'READ', b'Read'), (b'NEW', b'New')]),
        ),
    ]
