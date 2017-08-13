# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-01 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0030_auto_20170801_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='singleentry',
            name='action',
            field=models.CharField(choices=[('D', 'Debit'), ('C', 'Credit')], default='D', max_length=1),
            preserve_default=False,
        ),
    ]
