"""
All the tasks which are queued into django-q
    * User Triggered Async Tasks
    * Schedule Triggered Async Tasks
"""
import logging
from django_q.tasks import async_task
from apps.fyle.tasks import (
    import_credit_card_expenses,
    import_reimbursable_expenses
)
from apps.workspaces.models import Workspace
from apps.tasks.models import AccountingExport
from apps.fyle.helpers import assert_valid_request

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def queue_import_reimbursable_expenses(workspace_id: int, synchronous: bool = False):
    """
    Queue Import of Reimbursable Expenses from Fyle
    :param workspace_id: Workspace id
    :return: None
    """
    accounting_export, _ = AccountingExport.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_REIMBURSABLE_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    if not synchronous:
        async_task(
            'apps.fyle.tasks.import_reimbursable_expenses',
            workspace_id, accounting_export,
        )
        return

    import_reimbursable_expenses(workspace_id, accounting_export)


def queue_import_credit_card_expenses(workspace_id: int, synchronous: bool = False):
    """
    Queue Import of Credit Card Expenses from Fyle
    :param workspace_id: Workspace id
    :return: None
    """
    accounting_export, _ = AccountingExport.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_CREDIT_CARD_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    if not synchronous:
        async_task(
            'apps.fyle.tasks.import_credit_card_expenses',
            workspace_id, accounting_export,
        )
        return

    import_credit_card_expenses(workspace_id, accounting_export)


def async_handle_webhook_callback(body: dict, workspace_id: int) -> None:
    """
    Async'ly import and export expenses
    :param body: body
    :return: None
    """
    if body.get('action') == 'ACCOUNTING_EXPORT_INITIATED' and body.get('data'):
        org_id = body['data']['org_id']
        assert_valid_request(workspace_id=workspace_id, org_id=org_id)
        workspace = Workspace.objects.get(org_id=org_id)
        async_task('apps.workspaces.tasks.run_import_export', workspace.id)

    """for allowing expense edit, uncomment the below code and relevant test if required in future"""
    # elif body.get('action') == 'UPDATED_AFTER_APPROVAL' and body.get('data') and body.get('resource') == 'EXPENSE':
    #     org_id = body['data']['org_id']
    #     logger.info("| Updating non-exported expenses through webhook | Content: {{WORKSPACE_ID: {} Payload: {}}}".format(workspace_id, body.get('data')))
    #     assert_valid_request(workspace_id=workspace_id, org_id=org_id)
    #     async_task('apps.fyle.tasks.update_non_exported_expenses', body['data'])
