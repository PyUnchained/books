# Generated by Django 3.1.7 on 2021-03-04 03:43

import books.models.billing
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0038_auto_20210228_0348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaccount',
            name='start_date',
            field=models.DateField(default=books.models.billing.today),
        ),
    ]