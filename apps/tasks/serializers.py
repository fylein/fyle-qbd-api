from rest_framework import serializers

from .models import AccountingExport


class AccountingExportSerializer(serializers.ModelSerializer):
    """
    Task Log serializer
    """
    class Meta:
        model = AccountingExport
        fields = '__all__'
