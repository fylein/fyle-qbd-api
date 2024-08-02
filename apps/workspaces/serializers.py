"""
Workspace Serializers
"""
from typing import Dict
from rest_framework import serializers
from django_q.tasks import async_task
from django.core.cache import cache
from apps.mappings.models import QBDMapping
from fyle_rest_auth.helpers import get_fyle_admin
from fyle_rest_auth.models import AuthToken

from apps.fyle.helpers import get_cluster_domain
from quickbooks_desktop_api.utils import assert_valid

from .schedule import schedule_run_import_export
from .models import (
    FyleCredential,
    User,
    Workspace,
    ExportSettings,
    FieldMapping,
    AdvancedSetting
)

def pre_save_field_mapping_trigger(new_field_mapping: Dict, field_mapping: FieldMapping, workspace_id):
    item_type = new_field_mapping.get('item_type')
    if item_type and item_type != field_mapping.item_type and item_type in ['PROJECT', 'COST_CENTER']:
        QBDMapping.objects.filter(attribute_type=field_mapping.item_type, workspace_id=workspace_id).delete()


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """
    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = ('id', 'name', 'org_id', 'fyle_currency', 'app_version', 'created_at', 'updated_at', 'user')

    def create(self, validated_data):
        """
        Update workspace
        """
        access_token = self.context['request'].META.get('HTTP_AUTHORIZATION')
        user = self.context['request'].user
        
        # Getting user profile using the access token
        fyle_user = get_fyle_admin(access_token.split(' ')[1], None)

        # getting name, org_id, currency of Fyle User
        name = fyle_user['data']['org']['name']
        org_id = fyle_user['data']['org']['id']
        currency = fyle_user['data']['org']['currency']

        # Checking if workspace already exists
        workspace = Workspace.objects.filter(org_id=org_id).first()

        if workspace:
            # Adding user relation to workspace
            workspace.user.add(User.objects.get(user_id=user))
            workspace.org_id = org_id
            workspace.save()
            cache.delete(str(workspace.id))
        else:
            workspace = Workspace.objects.create(
                name=name, 
                org_id=org_id,
                currency=currency
            )

            workspace.user.add(User.objects.get(user_id=user))

            auth_tokens = AuthToken.objects.get(user__user_id=user)

            cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

            FyleCredential.objects.update_or_create(
                refresh_token=auth_tokens.refresh_token,
                workspace_id=workspace.id,
                cluster_domain=cluster_domain
            )

            FieldMapping.objects.update_or_create(
                workspace=workspace
            )
        
        return workspace


class ExportSettingsSerializer(serializers.ModelSerializer):
    """
    Export Settings serializer
    """
    class Meta:
        model = ExportSettings
        fields = '__all__'
        read_only_fields = ('id', 'workspace', 'created_at', 'updated_at')

    def create(self, validated_data):
        """
        Create Export Settings
        """
        assert_valid(validated_data, 'Body cannot be null')
        workspace_id = self.context['request'].parser_context.get('kwargs').get('workspace_id')

        export_settings = ExportSettings.objects.filter(
            workspace_id=workspace_id).first()

        export_settings, _ = ExportSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults=validated_data
        )

        # Update workspace onboarding state
        workspace = export_settings.workspace

        if workspace.onboarding_state == 'EXPORT_SETTINGS':
            workspace.onboarding_state = 'FIELD_MAPPINGS'
            workspace.save()
        
            async_task('apps.fyle.actions.sync_fyle_dimensions', workspace.id)

        return export_settings


class FieldMappingSerializer(serializers.ModelSerializer):
    """
    Field Mapping serializer
    """
    class Meta:
        model = FieldMapping
        fields = '__all__'
        read_only_fields = ('id', 'workspace', 'created_at', 'updated_at')

    def create(self, validated_data):
        """
        Create Field Mapping
        """
        workspace_id = self.context['request'].parser_context.get('kwargs').get('workspace_id')

        field_mapping = FieldMapping.objects.filter(
            workspace_id=workspace_id).first()

        field_mapping, _ = FieldMapping.objects.update_or_create(
            workspace_id=workspace_id,
            defaults=validated_data
        )

        """
        Remove the old mappings if the Item is mapped to some other field
        """
        pre_save_field_mapping_trigger(validated_data, field_mapping, workspace_id)

        # Update workspace onboarding state
        workspace = field_mapping.workspace

        if workspace.onboarding_state == 'FIELD_MAPPINGS':
            workspace.onboarding_state = 'ADVANCED_SETTINGS'
            workspace.save()
            """
            Sync dimension asyncly
            """
            async_task('apps.fyle.actions.sync_fyle_dimensions', workspace.id)

        return field_mapping

    def validate(self, data):
        """
        Check that item_type is not already used in project_type or class_type
        """
        item_type = data.get('item_type')
        project_type = data.get('project_type')
        class_type = data.get('class_type')

        if item_type in ['COST_CENTER', 'PROJECT']:
            # Checking if item_type is already used in project_type or class_type
            if item_type == project_type or item_type == class_type:
                raise serializers.ValidationError({
                    'item_type': 'This value is already used in project_type or class_type'
                })

        return data


class AdvancedSettingSerializer(serializers.ModelSerializer):
    """
    Advanced Settings serializer
    """
    class Meta:
        model = AdvancedSetting
        fields = '__all__'
        read_only_fields = ('id', 'workspace', 'created_at', 'updated_at')

    def create(self, validated_data):
        """
        Create Advanced Settings
        """
        workspace_id = self.context['request'].parser_context.get('kwargs').get('workspace_id')
        advanced_setting = AdvancedSetting.objects.filter(
            workspace_id=workspace_id).first()

        if not advanced_setting:
            if 'expense_memo_structure' not in validated_data:
                validated_data['expense_memo_structure'] = [
                    'employee_email',
                    'merchant',
                    'purpose',
                    'report_number'
                ]

        advanced_setting, _ = AdvancedSetting.objects.update_or_create(
            workspace_id=workspace_id,
            defaults=validated_data
        )

        # Schedule run import export or delete
        schedule_run_import_export(workspace_id)

        # Update workspace onboarding state
        workspace = advanced_setting.workspace

        if workspace.onboarding_state == 'ADVANCED_SETTINGS':
            workspace.onboarding_state = 'COMPLETE'
            workspace.save()
            async_task('apps.workspaces.tasks.async_create_admin_subcriptions', workspace_id)

        return advanced_setting
