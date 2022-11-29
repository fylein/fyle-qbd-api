# Generated by Django 3.1.14 on 2022-11-28 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FyleCredential',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('refresh_token', models.TextField(help_text='Stores Fyle refresh token')),
                ('cluster_domain', models.CharField(help_text='Cluster Domain', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at datetime')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at datetime')),
                ('workspace', models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, to='workspaces.workspace')),
            ],
            options={
                'db_table': 'fyle_credentials',
            },
        ),
    ]