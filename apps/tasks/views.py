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

        accounting_export_type = self.request.query_params.get('type', None)

        status = self.request.query_params.get('status', None)

        id = self.request.query_params.getlist('id')

        start_date = self.request.query_params.get('start_date', None)

        end_date = self.request.query_params.get('end_date', None)


        filters = {
            'workspace_id': workspace_id,
            'status__in': ['COMPLETE'],
        }

        if start_date and end_date:
            filters['updated_at__range'] = [start_date, end_date]

        if accounting_export_type:
            filters['type__in'] = accounting_export_type.split(',')

        if id:
            filters['id__in'] = id

        if status:
            filters['status__in'] = status.split(',')

        return AccountingExport.objects.filter(
            **filters
        ).all().order_by("-updated_at")


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
