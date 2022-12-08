from rest_framework import generics

from apps.tasks.serializers import AccountingExportSerializer

from .models import AccountingExport


class AccountingExportView(generics.ListAPIView):
    """
    Retrieve or Create Accounting Export
    """
    serializer_class = AccountingExportSerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    queryset = AccountingExport.objects.all()
