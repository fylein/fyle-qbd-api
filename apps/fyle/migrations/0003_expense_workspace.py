# Generated by Django 3.1.14 on 2022-12-01 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0005_exportsettings_credit_card_expense_date'),
        ('fyle', '0002_auto_20221130_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='workspace',
            field=models.ForeignKey(default=None, help_text='Workspace reference', on_delete=django.db.models.deletion.PROTECT, to='workspaces.workspace'),
            preserve_default=False,
        ),
    ]
