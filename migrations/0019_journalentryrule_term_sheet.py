# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-07-15 10:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0018_auto_20170715_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentryrule',
            name='term_sheet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.TermSheet'),
        ),
    ]