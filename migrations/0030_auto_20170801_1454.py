# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-01 14:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0029_auto_20170801_1444'),
    ]

    operations = [
        migrations.RenameField(
            model_name='journalentryaction',
            old_name='account',
            new_name='accounts',
        ),
    ]