# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0008_auto_20180411_1240'),
        ('notification', '0004_auto_20180419_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotificationDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_id', models.CharField(max_length=60)),
                ('device_type', models.IntegerField(blank=True, null=True, choices=[(0, b'iOS'), (1, b'Android')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(related_name='device_profile', to='profile.Profile')),
            ],
        ),
    ]
