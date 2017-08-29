# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notification_type', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=16, choices=[(b'READ', b'READ'), (b'NEW', b'NEW')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notifier', models.ForeignKey(related_name='notifier', to='profile.Profile')),
                ('recipient', models.ForeignKey(related_name='notification_received', to='profile.Profile')),
            ],
        ),
    ]
