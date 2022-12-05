from django.db import models
from django.db.models import JSONField

from apps.workspaces.models import Workspace



EXPORT_TYPE_CHOICES = (
    ('FETCHING_REIMBURSABLE_EXPENSES', 'FETCHING_REIMBURSABLE_EXPENSES'),
    ('FETCHING_CREDIT_CARD_EXPENSES', 'FETCHING_CREDIT_CARD_EXPENSES'),
    ('EXPORT_BILLS', 'EXPORT_BILLS'),
    ('EXPORT_CREDIT_CARD_PURCHASES', 'EXPORT_CREDIT_CARD_PURCHASES'),
    ('EXPORT_JOURNALS', 'EXPORT_JOURNALS')
)

STATUS_CHOICES  = (
    ('ENQUEUED', 'ENQUEUED'),
    ('IN_PROGRESS', 'IN_PROGRESS'),
    ('COMPLETE', 'COMPLETE'),
    ('FAILED', 'FAILED'),
    ('FATAL', 'FATAL')
)


class AccountingExport(models.Model):
    """
    Table to store export logs
    """
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(
        Workspace, 
        on_delete=models.PROTECT, 
        help_text='Reference to Workspace model'
    )
    type = models.CharField(max_length=50, choices=EXPORT_TYPE_CHOICES)
    file_id = models.CharField(max_length=255, null=True)
    task_id = models.CharField(max_length=255, null=True, help_text='Django Q task reference')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    errors = JSONField(help_text='Fatal Errors', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'accounting_exports'
