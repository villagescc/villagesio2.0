# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feeditem',
            name='item_type',
            field=models.CharField(max_length=16, choices=[(b'post', b'Post'), (b'listings', b'Listings'), (b'profile', b'Profile Update'), (b'acknowledgement', b'Acknowledgement'), (b'endorsement', b'Endorsement')]),
        ),
    ]
