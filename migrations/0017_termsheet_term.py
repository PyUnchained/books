# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-07-15 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0016_termsheet_interest_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='termsheet',
            name='term',
            field=models.IntegerField(default=90),
        ),
    ]
