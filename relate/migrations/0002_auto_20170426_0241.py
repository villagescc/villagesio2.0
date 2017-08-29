# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endorsement',
            name='weight',
            field=models.PositiveIntegerField(help_text="Each heart represents an hour of value you'd provide in exchange for acknowledgements.", verbose_name='Weight'),
        ),
    ]
