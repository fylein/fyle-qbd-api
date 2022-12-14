# Generated by Django 3.1.14 on 2022-12-05 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_accountingexport_file_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountingexport',
            name='type',
            field=models.CharField(choices=[('FETCHING_REIMBURSABLE_EXPENSES', 'FETCHING_REIMBURSABLE_EXPENSES'), ('FETCHING_CREDIT_CARD_EXPENSES', 'FETCHING_CREDIT_CARD_EXPENSES'), ('EXPORT_BILLS', 'EXPORT_BILLS'), ('EXPORT_CREDIT_CARD_PURCHASES', 'EXPORT_CREDIT_CARD_PURCHASES'), ('EXPORT_JOURNALS', 'EXPORT_JOURNALS')], max_length=50),
        ),
    ]
