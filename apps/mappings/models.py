from django.db import models
from typing import List, Dict

from apps.workspaces.models import Workspace

class QBDMapping(models.Model):
    """
    Fyle Expense Attributes
    """
    id = models.AutoField(primary_key=True)
    attribute_type = models.CharField(max_length=255, help_text='Type of expense attribute')
    source_value = models.CharField(max_length=1000, help_text='Value of expense attribute')
    source_id = models.CharField(max_length=255, help_text='Fyle ID')
    destination_value = models.CharField(max_length=1000, null=True, blank=True, help_text='Value of destination attribute')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'qbd_mappings'

    @staticmethod
    def update_or_create_mapping_objects(qbd_mapping_objects: List[Dict],workspace_id: int):
        for qbd_mapping_object in qbd_mapping_objects:
            qbd_mapping, _ = QBDMapping.objects.update_or_create(
                workspace_id= workspace_id,
                source_value= qbd_mapping_object['value'],
                attribute_type= qbd_mapping_object['attribute_type'],
                defaults={
                    'source_id': qbd_mapping_object['source_id'],
                }
            )