# Generated by Django 3.1.14 on 2023-10-06 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0025_auto_20230823_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportsettings',
            name='is_simplify_report_closure_enabled',
            field=models.BooleanField(default=True, help_text='Simplify report closure is enabled'),
        ),
    ]
