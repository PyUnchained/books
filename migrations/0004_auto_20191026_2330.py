# Generated by Django 2.2.6 on 2019-10-26 23:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_systemaccount_initial_setup_done'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='system_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount'),
        ),
    ]