# Generated by Django 3.1.14 on 2022-12-07 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0016_auto_20221207_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportsettings',
            name='credit_card_expense_date',
            field=models.CharField(choices=[('last_spent_at', 'last_spent_at'), ('spent_at', 'spent_at'), ('created_at', 'created_at')], max_length=255, null=True),
        ),
    ]
