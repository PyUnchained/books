# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-07-15 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0017_termsheet_term'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settlement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('term', models.IntegerField(default=90)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Account')),
            ],
        ),
        migrations.RemoveField(
            model_name='termsheet',
            name='term',
        ),
        migrations.AddField(
            model_name='settlement',
            name='term_sheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.TermSheet'),
        ),
    ]
