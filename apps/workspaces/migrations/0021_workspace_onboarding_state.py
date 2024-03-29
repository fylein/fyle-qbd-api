# Generated by Django 3.1.14 on 2023-02-07 08:39

from django.db import migrations, models
import apps.workspaces.models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0020_advancedsetting_time_of_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspace',
            name='onboarding_state',
            field=models.CharField(
                choices=[
                    ('CONNECTION', 'CONNECTION'),
                    ('EXPORT_SETTINGS', 'EXPORT_SETTINGS'),
                    ('FIELD_MAPPINGS', 'FIELD_MAPPINGS'),
                    ('ADVANCED_SETTINGS', 'ADVANCED_SETTINGS'),
                    ('COMPLETE', 'COMPLETE')
                ],
                default=apps.workspaces.models.get_default_onboarding_state,
                help_text='Onboarding status of the workspace',
                max_length=50, null=True
            ),
        ),
    ]
