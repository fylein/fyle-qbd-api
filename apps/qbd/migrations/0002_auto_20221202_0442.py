# Generated by Django 3.1.14 on 2022-12-02 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qbd', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billlineitem',
            name='class_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='billlineitem',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]