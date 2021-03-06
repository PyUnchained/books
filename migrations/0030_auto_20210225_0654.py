# Generated by Django 3.1.7 on 2021-02-25 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0029_auto_20210225_0600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingmethod',
            name='day_of_month',
        ),
        migrations.RemoveField(
            model_name='billingmethod',
            name='time',
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='last_billed',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='billingmethod',
            name='billing_period',
            field=models.IntegerField(default=1, help_text='Duration in months between charges.'),
        ),
    ]
