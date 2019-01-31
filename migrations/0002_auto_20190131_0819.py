# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-31 06:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singleentry',
            name='journal_entry',
        ),
        migrations.AddField(
            model_name='singleentry',
            name='details',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='credit_acc',
            field=models.ManyToManyField(blank=True, related_name='credit_entry', to='books.Account', verbose_name='credit'),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='debit_acc',
            field=models.ManyToManyField(blank=True, related_name='debit_entry', to='books.Account', verbose_name='debit'),
        ),
    ]