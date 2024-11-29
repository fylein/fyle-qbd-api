# Generated by Django 3.1.14 on 2024-09-12 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotlight', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CopyExportSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workspace_id', models.IntegerField(help_text='Workspace id of the organization')),
                ('reimbursable_export_setting', models.JSONField(null=True)),
                ('ccc_export_setting', models.JSONField(null=True)),
            ],
            options={
                'db_table': 'copy_export_settings',
            },
        ),
    ]
