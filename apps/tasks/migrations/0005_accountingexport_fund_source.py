# Generated by Django 3.1.14 on 2023-02-20 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20221205_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountingexport',
            name='fund_source',
            field=models.CharField(choices=[('PERSONAL', 'PERSONAL'), ('CCC', 'CCC')], default='CCC', max_length=50),
        ),
    ]
