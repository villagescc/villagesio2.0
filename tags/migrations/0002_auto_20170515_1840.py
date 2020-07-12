# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0004_profile_job'),
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taglisting',
            name='listing',
        ),
        migrations.RemoveField(
            model_name='taglisting',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='tagprofile',
            name='profile',
        ),
        migrations.AddField(
            model_name='tagprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tagprofile',
            name='profile_id',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='tag_profile', blank=True, to='profile.Profile', null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=10),
        ),
        migrations.RemoveField(
            model_name='tagprofile',
            name='tag',
        ),
        migrations.AddField(
            model_name='tagprofile',
            name='tag',
            field=models.ManyToManyField(to='tags.Tag'),
        ),
        migrations.DeleteModel(
            name='TagListing',
        ),
    ]
