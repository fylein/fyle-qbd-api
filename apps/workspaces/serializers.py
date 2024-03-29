"""
Workspace Serializers
"""
from rest_framework import serializers

from django.core.cache import cache
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

        # Update workspace onboarding state
        workspace = field_mapping.workspace

        if workspace.onboarding_state == 'FIELD_MAPPINGS':
            workspace.onboarding_state = 'ADVANCED_SETTINGS'
            workspace.save()

        return field_mapping


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

        return advanced_setting
