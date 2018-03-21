# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-30 12:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0027_auto_20170718_0933'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountSubType',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='journalcreationrule',
            name='preset',
            field=models.CharField(blank=True, choices=[('TB', 'Trial Balance'), ('BS', 'Balance Sheet'), ('CB', 'Cash Book')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='sub_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.AccountSubType'),
        ),
    ]