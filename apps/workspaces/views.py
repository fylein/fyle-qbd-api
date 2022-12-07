from rest_framework import generics

from apps.workspaces.models import Workspace
from apps.workspaces.serializers import WorkspaceSerializer
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
