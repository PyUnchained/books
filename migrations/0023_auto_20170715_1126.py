# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-07-15 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0022_auto_20170715_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='term',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='termsheet',
            name='default_discount_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Yearly Default Discount Rate (%)'),
        ),
        migrations.AlterField(
            model_name='termsheet',
            name='discount_rate',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Yearly Discount Rate (%)'),
        ),
        migrations.AlterField(
            model_name='termsheet',
            name='interest_method',
            field=models.CharField(choices=[('S', 'Simple'), ('C', 'Compound')], default='S', max_length=2),
        ),
        migrations.AlterField(
            model_name='termsheet',
            name='rollover_discount_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Yearly Rollover Discount Rate (%)'),
        ),
    ]
