# Generated by Django 2.2.6 on 2020-01-24 00:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_doubleentry_account'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doubleentry',
            name='account',
        ),
        migrations.AddField(
            model_name='doubleentry',
            name='system_account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount'),
            preserve_default=False,
        ),
    ]
