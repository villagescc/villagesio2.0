# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('listings', '0007_auto_20170509_0432'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagListing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='listings',
            name='tags',
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to='tags.Tag', null=True),
        ),
        migrations.AddField(
            model_name='taglisting',
            name='listing_id',
            field=models.ForeignKey(on_delete=models.CASCADE, to='listings.Listings'),
        ),
        migrations.AddField(
            model_name='taglisting',
            name='tag',
            field=models.ManyToManyField(default=None, to='tags.Tag'),
        ),
    ]
