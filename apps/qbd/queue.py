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
    print('queue_create_bills_iif_file')
    accounting_export = AccountingExport.objects.create(
        workspace_id=workspace_id,
        type='EXPORT_BILLS',
        status='ENQUEUED',
        fund_source='PERSONAL'
    )

    async_task('apps.qbd.tasks.create_bills_iif_file', workspace_id, accounting_export)


def queue_create_credit_card_purchases_iif_file(workspace_id: int):
    """
    Queue Create Credit Card Purchases IIF File
    :param workspace_id: Workspace id
    :return: None
    """
    accounting_export = AccountingExport.objects.create(
        workspace_id=workspace_id,
        type='EXPORT_CREDIT_CARD_PURCHASES',
        status='ENQUEUED',
        fund_source='CCC'
    )

    async_task('apps.qbd.tasks.create_credit_card_purchases_iif_file', workspace_id, accounting_export)


def queue_create_journals_iif_file(fund_source: str, workspace_id: int):
    """
    Queue Create Journals IIF File
    :param fund_source: Fund Source
    :param workspace_id: Workspace id
    :return: None
    """
    accounting_export = AccountingExport.objects.create(
        workspace_id=workspace_id,
        type='EXPORT_JOURNALS',
        status='ENQUEUED',
        fund_source=fund_source
    )

    async_task(
        'apps.qbd.tasks.create_journals_iif_file', workspace_id, accounting_export, fund_source
    )
