# Generated by Django 3.1.14 on 2023-02-08 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0022_auto_20230207_0846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advancedsetting',
            name='emails_selected',
        ),
        migrations.AddField(
            model_name='advancedsetting',
            name='emails_selected',
            field=models.JSONField(default=list, help_text='Emails Selected For Email Notification', null=True),
        ),
    ]
