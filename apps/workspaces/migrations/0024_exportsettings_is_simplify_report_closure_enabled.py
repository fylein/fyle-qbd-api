# Generated by Django 3.1.14 on 2023-05-04 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0023_auto_20230208_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportsettings',
            name='is_simplify_report_closure_enabled',
            field=models.BooleanField(default=False, help_text='Simplify report closure is enabled'),
        ),
    ]
