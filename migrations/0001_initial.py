# Generated by Django 2.2.6 on 2020-01-18 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=120, verbose_name='account name')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AccountSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('financial_year_start', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='SingleEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(blank=True, choices=[('D', 'Debit'), ('C', 'Credit')], max_length=1)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('details', models.CharField(max_length=300)),
                ('date', models.DateField()),
                ('account', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='books.Account')),
            ],
            options={
                'verbose_name_plural': 'Single Entries',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SystemAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of business', max_length=200)),
                ('password', models.CharField(max_length=300)),
                ('email', models.EmailField(help_text='Used to login \n        as administrator.', max_length=254)),
                ('initial_setup_done', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('settings', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='books.AccountSettings')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=150)),
                ('credit_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credi_transaction_definitions', to='books.Account')),
                ('debit_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debit_transaction_definitions', to='books.Account')),
                ('system_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_transaction', to='books.SingleEntry')),
                ('debit_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debit_transaction', to='books.SingleEntry')),
                ('definition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.TransactionDefinition')),
                ('system_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount')),
            ],
        ),
        migrations.AddField(
            model_name='singleentry',
            name='system_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount'),
        ),
        migrations.CreateModel(
            name='DeclaredSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('credit', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('details', models.CharField(max_length=140)),
                ('date', models.DateField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Account')),
                ('system_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount')),
            ],
        ),
        migrations.CreateModel(
            name='AccountGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=300, null=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='books.AccountGroup')),
                ('system_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'system_account')},
            },
        ),
        migrations.AddField(
            model_name='account',
            name='account_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.AccountGroup'),
        ),
        migrations.AddField(
            model_name='account',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='books.Account', verbose_name='parent account'),
        ),
        migrations.AddField(
            model_name='account',
            name='system_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.SystemAccount'),
        ),
    ]
