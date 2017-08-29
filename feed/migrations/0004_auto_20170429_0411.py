# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feeditem',
            name='item_type',
            field=models.CharField(max_length=16, choices=[(b'post', b'Post'), (b'profile', b'Profile Update'), (b'acknowledgement', b'Acknowledgement'), (b'endorsement', b'Endorsement')]),
        ),
    ]
