# Generated by Django 3.1.14 on 2023-01-19 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0019_auto_20230119_0601'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsetting',
            name='time_of_day',
            field=models.TimeField(help_text='Time of day for schedule', null=True),
        ),
    ]
