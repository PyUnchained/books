# Generated by Django 2.2.6 on 2020-01-23 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemaccount',
            name='email',
            field=models.EmailField(blank=True, help_text='Used to login \n        as administrator.', max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='systemaccount',
            name='password',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]