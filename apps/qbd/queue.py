"""
All the tasks which are queued into django-q
    * User Triggered Async Tasks
    * Schedule Triggered Async Tasks
"""
from django_q.tasks import async_task

from apps.tasks.models import AccountingExport


def queue_create_bills_iif_file(workspace_id: int):
    """
    Queue Create Bills IIF File
    :param workspace_id: Workspace id
    :return: None
    """
    accounting_export = AccountingExport.objects.create(
        workspace_id=workspace_id,
        type='EXPORT_BILLS',
        status='ENQUEUED'
    )

    async_task('apps.qbd.tasks.create_bills_iif_file', workspace_id, accounting_export)
