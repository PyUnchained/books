# Generated by Django 3.0.6 on 2021-02-23 06:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0027_auto_20210222_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingmethod',
            name='periodic_task',
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='charge',
            field=models.DecimalField(decimal_places=2, default=20.0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='start_date',
            field=models.DateField(default=datetime.date(2021, 2, 23)),
            preserve_default=False,
        ),
    ]