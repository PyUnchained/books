# Generated by Django 3.0.6 on 2020-11-09 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0022_auto_20201109_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactiondefinition',
            name='short_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
