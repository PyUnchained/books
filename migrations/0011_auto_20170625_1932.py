# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-25 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_auto_20170625_0543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalcreationrule',
            name='reversed_credit_entries',
            field=models.ManyToManyField(blank=True, help_text=b'Reversed entries will appear on the debit side of the journal.', related_name='reversed_credit_entries', to='books.Account'),
        ),
        migrations.AlterField(
            model_name='journalcreationrule',
            name='reversed_debit_entries',
            field=models.ManyToManyField(blank=True, help_text=b'Reversed entries will appear on the credit side of the journal.', related_name='reversed_debit_entries', to='books.Account'),
        ),
    ]