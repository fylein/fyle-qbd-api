from rest_framework import generics
from rest_framework.views import Response, status

from quickbooks_desktop_api.utils import assert_valid

from apps.workspaces.models import (
    Workspace, ExportSettings,
    FieldMapping, AdvancedSetting
)
from apps.workspaces.serializers import (
    WorkspaceSerializer, ExportSettingsSerializer,
    FieldMappingSerializer, AdvancedSettingSerializer
)
from .tasks import run_import_export


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


class TriggerExportView(generics.CreateAPIView):
    """
    Trigger Export
    """

    def post(self, request, *args, **kwargs):
        """
        Trigger Export
        """
        workspace_id = self.kwargs.get('workspace_id')

        run_import_export(workspace_id=workspace_id)

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'Export triggered successfully'
            }
        )

class ReadyView(generics.RetrieveAPIView):
    """
    Ready call to check if the api is ready
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Ready call
        """
        Workspace.objects.first()

        return Response(
            data={
                'message': 'Ready'
            },
            status=status.HTTP_200_OK
        )
