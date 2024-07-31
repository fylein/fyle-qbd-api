from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.exceptions import handle_view_exceptions
from apps.fyle.queue import async_handle_webhook_callback
from apps.mappings.connector import PlatformConnector
from apps.workspaces.models import FyleCredential

from .actions import sync_fyle_dimensions


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """
        sync_fyle_dimensions(workspace_id=kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class WebhookCallbackView(generics.CreateAPIView):
    """
    Export View
    """
    authentication_classes = []
    permission_classes = []

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        async_handle_webhook_callback(request.data, int(kwargs['workspace_id']))

        return Response(data={}, status=status.HTTP_200_OK)


class CustomFieldView(generics.RetrieveAPIView):
    """
    Custom Field view
    """
    def get(self, request, *args, **kwargs):
        """
        Get Custom Fields
        """
        query = {
        'order': 'updated_at.desc',
        'is_custom': 'eq.true',
        'type': 'eq.SELECT',
        'is_enabled': 'eq.true'
        }
        
        workspace_id = self.kwargs['workspace_id']
        platform_connector = PlatformConnector(workspace_id)
        custom_field_gen = platform_connector.platform.v1beta.admin.expense_fields.list_all(query)
        
        distinct_custom_fields = []
        
        for custom_fields in custom_field_gen:
            for custom_field in custom_fields.get('data'):
                distinct_custom_fields.append(custom_field['field_name'])

        return Response(
            data=distinct_custom_fields,
            status=status.HTTP_200_OK
        )