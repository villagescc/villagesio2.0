# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0005_auto_20171004_1934'),
        ('profile', '0005_profile_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilePageTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('listing_type', models.CharField(max_length=100, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='tag',
        ),
        migrations.AddField(
            model_name='profilepagetag',
            name='profile',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='profile', to='profile.Profile'),
        ),
        migrations.AddField(
            model_name='profilepagetag',
            name='tag',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='profile_tag', blank=True, to='tags.Tag', null=True),
        ),
    ]
