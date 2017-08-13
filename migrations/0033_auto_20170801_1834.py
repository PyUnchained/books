# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-01 18:34
from __future__ import unicode_literals

import books.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0032_remove_journalentry_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='date_from',
            field=models.DateField(default=books.models.today),
        ),
        migrations.AddField(
            model_name='journal',
            name='date_to',
            field=models.DateField(default=books.models.year_ago),
        ),
        migrations.AddField(
            model_name='journal',
            name='preset',
            field=models.CharField(blank=True, choices=[('TB', 'Trial Balance'), ('BS', 'Balance Sheet'), ('CB', 'Cash Book')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='journal',
            name='rule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.JournalCreationRule'),
        ),
    ]
