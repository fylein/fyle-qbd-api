# Generated by Django 3.1.14 on 2022-12-06 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0008_auto_20221206_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportsettings',
            name='credit_card_expense_date',
            field=models.CharField(choices=[('LAST_SPEND_DATE', 'last_spent_at'), ('CREATED_DATE', 'created_at'), ('SPEND DATE', 'spent_at'), ('CURRENT_DATE', 'current_date')], max_length=255),
        ),
    ]
