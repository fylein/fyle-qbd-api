from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.exceptions import handle_view_exceptions
from apps.fyle.queue import async_handle_webhook_callback

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
