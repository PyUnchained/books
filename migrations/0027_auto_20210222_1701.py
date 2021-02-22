# Generated by Django 3.0.6 on 2021-02-22 15:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_celery_beat', '0012_periodictask_expire_seconds'),
        ('books', '0026_auto_20201215_0356'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('up_to_date', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due', models.DateTimeField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=20)),
                ('paid', models.BooleanField()),
                ('file', models.FileField(upload_to='books/generated/invoices')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('billing_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.BillingAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='books/generated/receipts')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='BillingMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('time', models.TimeField()),
                ('day_of_month', models.IntegerField(default=1)),
                ('billing_period', models.IntegerField(default=1)),
                ('grace_period', models.IntegerField(default=14)),
                ('periodic_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.PeriodicTask')),
            ],
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='billing_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.BillingMethod'),
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
