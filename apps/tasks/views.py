from rest_framework import generics
from rest_framework.views import Response, status

from quickbooks_desktop_api.utils import assert_valid

from apps.tasks.serializers import AccountingExportSerializer
from apps.fyle.helpers import download_iif_file

from .models import AccountingExport


class AccountingExportView(generics.ListAPIView):
    """
    Retrieve or Create Accounting Export
    """
    serializer_class = AccountingExportSerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')

        type = self.request.query_params.getlist('type')

        status = self.request.query_params.getlist('status', ['COMPLETE'])

        id = self.request.query_params.getlist('id')

        filters = {
            'workspace_id': workspace_id,
            'status__in': status,
        }

        if type:
            filters['type__in'] = type
        
        if id:
            filters['id__in'] = id

        return AccountingExport.objects.filter(
            **filters
        ).all()


class AccountingExportDownloadView(generics.CreateAPIView):
    """
    Download Accounting Export
    """
    serializer_class = AccountingExportSerializer
    
    def post(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get('workspace_id')
        accounting_export_id = self.kwargs.get('accounting_export_id')

        accounting_export = AccountingExport.objects.filter(
            workspace_id=workspace_id,
            id=accounting_export_id
        ).first()

        assert_valid(
            accounting_export is not None, 
            'Accounting Export not found with id: {}'.format(accounting_export_id)
        )

        file_id = accounting_export.file_id

        download_url = download_iif_file(file_id, workspace_id)

        return Response(
            data={
                'download_url': download_url,
                'file_id': file_id,
                'accounting_export_id': accounting_export_id,
                'workspace_id': workspace_id
            },
            status=status.HTTP_200_OK
        )
