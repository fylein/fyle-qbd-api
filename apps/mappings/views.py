from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.mappings.serializers import QBDMappingSerializer
from quickbooks_desktop_api.utils import assert_valid, LookupFieldMixin

from .models import QBDMapping
from .tasks import sync_attributes
from .actions import qbd_mapping_stat


class QBDMappingView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    QBD Mapping Update View
    """
    
    queryset = QBDMapping.objects.all()
    serializer_class = QBDMappingSerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'attribute_type': {'exact'},'destination_value': {'isnull'}}
    ordering_fields = ('source_value',)

    def get(self, request, *args, **kwargs):
        attribute_type = self.request.query_params.get('attribute_type')
        workspace_id= self.kwargs['workspace_id']
        qbd_mapping_count = QBDMapping.objects.filter(
            workspace_id = workspace_id).count()

        if qbd_mapping_count == 0:
            sync_attributes(attribute_type, workspace_id)

        return self.list(request, *args, **kwargs)


#mapping stats view
class QBDMappingStatsView(generics.RetrieveAPIView):
    """
    Stats for total mapped and unmapped count for a given attribute type
    """

    def get(self, request, *args, **kwargs):
        source_type = self.request.query_params.get('source_type')
        workspace_id= self.kwargs['workspace_id']

        assert_valid(source_type is not None, 'query param source_type not found')

        stat_response = qbd_mapping_stat(source_type, workspace_id)

        return Response(
            data=stat_response,
            status=status.HTTP_200_OK
        )    
