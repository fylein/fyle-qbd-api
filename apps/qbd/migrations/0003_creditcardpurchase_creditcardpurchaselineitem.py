# Generated by Django 3.1.14 on 2022-12-05 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0003_expense_workspace'),
        ('tasks', '0003_accountingexport_file_id'),
        ('workspaces', '0006_auto_20221202_1146'),
        ('qbd', '0002_auto_20221202_0442'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditCardPurchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_type', models.CharField(default='TRNS', max_length=255)),
                ('transaction_id', models.CharField(default='', max_length=255)),
                ('transaction_type', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
                ('account', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('class_name', models.CharField(max_length=255, null=True)),
                ('amount', models.FloatField(help_text='Credit Card amount')),
                ('document_number', models.CharField(default='', max_length=255, null=True)),
                ('memo', models.TextField()),
                ('clear', models.CharField(default='', max_length=255)),
                ('to_print', models.CharField(default='', max_length=255)),
                ('name_is_taxable', models.CharField(default='', max_length=255)),
                ('address_1', models.CharField(default='', max_length=255)),
                ('address_2', models.CharField(default='', max_length=255)),
                ('address_3', models.CharField(default='', max_length=255)),
                ('address_4', models.CharField(default='', max_length=255)),
                ('address_5', models.CharField(default='', max_length=255)),
                ('due_date', models.CharField(default='', max_length=255)),
                ('terms', models.CharField(default='', max_length=255)),
                ('paid', models.CharField(default='', max_length=255)),
                ('ship_via', models.CharField(default='', max_length=255)),
                ('ship_date', models.CharField(default='', max_length=255)),
                ('year_to_date', models.CharField(default='', max_length=255)),
                ('wage_base', models.CharField(default='', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('accounting_export', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='credit_card_purchases', to='tasks.accountingexport')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_card_purchases', to='workspaces.workspace')),
            ],
            options={
                'db_table': 'credit_card_purchases',
            },
        ),
        migrations.CreateModel(
            name='CreditCardPurchaseLineitem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_type', models.CharField(default='SPL', max_length=255)),
                ('split_line_id', models.CharField(default='', max_length=255)),
                ('transaction_type', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
                ('account', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, null=True)),
                ('class_name', models.CharField(max_length=255, null=True)),
                ('amount', models.FloatField(help_text='Credit Card amount')),
                ('document_number', models.CharField(default='', max_length=255, null=True)),
                ('memo', models.TextField()),
                ('clear', models.CharField(default='', max_length=255)),
                ('quantity', models.CharField(default='', max_length=255)),
                ('price', models.CharField(default='', max_length=255)),
                ('inventory_item', models.CharField(default='', max_length=255)),
                ('payment_method', models.CharField(default='', max_length=255)),
                ('taxable', models.CharField(default='', max_length=255)),
                ('value_adjustment', models.CharField(default='', max_length=255)),
                ('reimbursable_expense', models.CharField(max_length=255)),
                ('service_date', models.CharField(default='', max_length=255)),
                ('others_2', models.CharField(default='', max_length=255)),
                ('others_3', models.CharField(default='', max_length=255)),
                ('year_to_date', models.CharField(default='', max_length=255)),
                ('wage_base', models.CharField(default='', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('credit_card_purchase', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lineitems', to='qbd.creditcardpurchase')),
                ('expense', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='credit_card_purchase_lineitems', to='fyle.expense')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_card_purchase_lineitems', to='workspaces.workspace')),
            ],
            options={
                'db_table': 'credit_card_purchase_lineitems',
            },
        ),
    ]
