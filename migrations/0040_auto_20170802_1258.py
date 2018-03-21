# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-02 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0039_auto_20170802_1233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='singleentry',
            options={'verbose_name_plural': 'Single Entries'},
        ),
        migrations.AddField(
            model_name='journalentryaction',
            name='sub_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.AccountSubType'),
        ),
        migrations.AlterField(
            model_name='journalcreationrule',
            name='preset',
            field=models.CharField(choices=[('TB', 'Trial Balance'), ('BS', 'Balance Sheet'), ('CB', 'Cash Book'), ('PL', 'Trading, Profit & Loss'), ('T', 'Generic T-Account')], max_length=2, null=True),
        ),
    ]