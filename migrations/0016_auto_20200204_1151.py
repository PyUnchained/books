# Generated by Django 2.2.6 on 2020-02-04 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_doubleentry_creator_ref'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doubleentry',
            name='creator_ref',
            field=models.CharField(blank=True, editable=False, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='singleentry',
            name='creator_ref',
            field=models.CharField(blank=True, editable=False, max_length=200, null=True),
        ),
    ]
