# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-18 11:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_singleentry_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='singleentry',
            options={'ordering': ['-date'], 'verbose_name_plural': 'Single Entries'},
        ),
    ]