from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.mappings.tasks import sync_attributes


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """
        sync_attributes('CORPORATE_CARD', workspace_id=kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)
