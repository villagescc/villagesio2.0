# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relate', '0003_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('recipient', models.ForeignKey(on_delete=models.CASCADE, related_name='referral_received', to='profile.Profile')),
                ('referrer', models.ForeignKey(on_delete=models.CASCADE, related_name='referral_made', to='profile.Profile')),
            ],
        ),
    ]
