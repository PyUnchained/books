# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-31 06:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20190131_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='singleentry',
            name='date',
            field=models.DateField(default=datetime.date(2019, 1, 31)),
            preserve_default=False,
        ),
    ]