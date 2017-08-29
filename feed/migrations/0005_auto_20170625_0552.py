# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0004_auto_20170429_0411'),
    ]

    operations = [
        migrations.AddField(
            model_name='feeditem',
            name='balance',
            field=models.DecimalField(default=0, null=True, max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='feeditem',
            name='referral_count',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='feeditem',
            name='item_type',
            field=models.CharField(max_length=16, choices=[(b'post', b'Post'), (b'profile', b'Profile Update'), (b'acknowledgement', b'Acknowledgement'), (b'endorsement', b'Endorsement'), (b'referral', b'Referral')]),
        ),
    ]
