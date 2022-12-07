from rest_framework import generics

from apps.workspaces.models import (
    Workspace, ExportSettings,
    FieldMapping, AdvancedSetting
)
from apps.workspaces.serializers import (
    WorkspaceSerializer, ExportSettingsSerializer,
    FieldMappingSerializer, AdvancedSettingSerializer
)
from quickbooks_desktop_api.utils import assert_valid

class WorkspaceView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Create Retrieve Workspaces
    """
    serializer_class = WorkspaceSerializer

    permission_classes = []

    def get_object(self):
        """
        return workspace object for the given org_id
        """
        org_id = self.request.query_params.get('org_id')

        assert_valid(org_id is not None, 'org_id is missing')

        workspace = Workspace.objects.filter(org_id=org_id).first()

        assert_valid(workspace is not None, 'Workspace not found')

        return workspace


class ExportSettingView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Retrieve or Create Export Settings
    """
    serializer_class = ExportSettingsSerializer
    lookup_field = 'workspace_id'

    queryset = ExportSettings.objects.all()


class FieldMappingView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Retrieve or Create Field Mapping
    """
    serializer_class = FieldMappingSerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    queryset = FieldMapping.objects.all()


class AdvancedSettingView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Retrieve or Create Advanced Settings
    """
    serializer_class = AdvancedSettingSerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    queryset = AdvancedSetting.objects.all()
