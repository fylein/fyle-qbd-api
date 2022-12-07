# Generated by Django 3.1.14 on 2022-12-07 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0013_auto_20221207_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportsettings',
            name='credit_card_expense_export_type',
            field=models.CharField(choices=[('JOURNAL_ENTRY', 'JOURNAL_ENTRY'), ('CREDIT_CARD_PURCHASE', 'CREDIT_CARD_PURCHASE')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='exportsettings',
            name='reimbursable_expenses_export_type',
            field=models.CharField(choices=[('BILL', 'BILL'), ('JOURNAL_ENTRY', 'JOURNAL_ENTRY')], max_length=255, null=True),
        ),
    ]
