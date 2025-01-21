import json
import logging
from datetime import datetime, timezone

from django.conf import settings
from django_q.tasks import async_task
from django_q.models import Schedule
from fyle_rest_auth.helpers import get_fyle_admin

from apps.fyle.queue import queue_import_credit_card_expenses, queue_import_reimbursable_expenses
from apps.qbd.queue import (
    queue_create_bills_iif_file,
    queue_create_credit_card_purchases_iif_file,
    queue_create_journals_iif_file
)
from apps.tasks.models import AccountingExport
from apps.fyle.models import Expense
from apps.workspaces.models import FyleCredential, ExportSettings, Workspace, AdvancedSetting
from fyle_integrations_platform_connector import PlatformConnector
from apps.fyle.helpers import post_request, validate_webhook_request


logger = logging.getLogger(__name__)
logger.level = logging.INFO


def run_import_export(workspace_id: int):
    """
    Run Processes to Generate IIF File
    :param workspace_id: Workspace id
    """
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.migrated_to_qbd_direct:
        logger.error("Import Export not running since the workspace with id {} is migrated to QBD Connector".format(workspace.id))
        return

    export_settings = ExportSettings.objects.get(workspace_id=workspace_id)

    # For Reimbursable Expenses
    if export_settings.reimbursable_expenses_export_type:
        queue_import_reimbursable_expenses(workspace_id, synchronous=True)

        accounting_export = AccountingExport.objects.get(
            workspace_id=workspace_id,
            type='FETCHING_REIMBURSABLE_EXPENSES'
        )
        
        if accounting_export.status == 'COMPLETE':
            expenses = Expense.objects.filter(
                workspace_id=workspace_id,
                exported=False,
                fund_source='PERSONAL'
            )

            if expenses.count():
                if export_settings.reimbursable_expenses_export_type == 'BILL':
                    queue_create_bills_iif_file(workspace_id)

                elif export_settings.reimbursable_expenses_export_type == 'JOURNAL_ENTRY':
                    queue_create_journals_iif_file('PERSONAL', workspace_id)
    
    # For Credit Card Expenses
    if export_settings.credit_card_expense_export_type:
        queue_import_credit_card_expenses(workspace_id, synchronous=True)

        accounting_export = AccountingExport.objects.get(
            workspace_id=workspace_id,
            type='FETCHING_CREDIT_CARD_EXPENSES'
        )

        if accounting_export.status == 'COMPLETE':
            expenses = Expense.objects.filter(
                workspace_id=workspace_id,
                exported=False,
                fund_source='CCC'
            )

            if expenses.count():
                if export_settings.credit_card_expense_export_type == 'CREDIT_CARD_PURCHASE':
                    queue_create_credit_card_purchases_iif_file(workspace_id)

                elif export_settings.credit_card_expense_export_type == 'JOURNAL_ENTRY':
                    queue_create_journals_iif_file('CCC', workspace_id)

    async_task('apps.workspaces.tasks.async_update_timestamp_in_qbd_direct', workspace_id=workspace_id)


def async_update_workspace_name(workspace: Workspace, access_token: str):
    """
    Update Workspace Name

    :param workspace: Workspace object
    :param access_token: Fyle access token
    """
    fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
    org_name = fyle_user['data']['org']['name']

    workspace.name = org_name
    workspace.save()


def async_create_admin_subcriptions(workspace_id: int) -> None:
    """
    Create admin subscriptions
    :param workspace_id: workspace id
    :return: None
    """
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    payload = {
        'is_enabled': True,
        'webhook_url': '{}/workspaces/{}/fyle/webhook_callback/'.format(settings.API_URL, workspace_id)
    }
    platform.subscriptions.post(payload)


def async_handle_webhook_callback(payload: dict) -> None:
    """
    Handle webhook callback
    :param data: data
    :return: None
    """
    logger.info("Received Webhook Callback with payload: %s", payload)

    org_id = payload.get('data', {}).get('org_id')
    action = payload.get('action')
    validate_webhook_request(org_id=org_id, action=action)

    if action == 'DISABLE_EXPORT':
        workspace = Workspace.objects.filter(org_id=org_id).first()
        if workspace:
            workspace.migrated_to_qbd_direct = True
            workspace.updated = datetime.now(timezone.utc)
            workspace.save(update_fields=['migrated_to_qbd_direct', 'updated_at'])

            Schedule.objects.filter(args=str(workspace.id)).all().delete()
            adv_settings = AdvancedSetting.objects.filter(workspace_id=workspace.id, schedule_id__isnull=False).first()
            if adv_settings:
                adv_settings.schedule_id = None
                adv_settings.save(update_fields=['schedule_id'])
        else:
            logger.warning('Webhook Callback: Workspace not found for org_id: {}'.format(org_id))


def async_update_timestamp_in_qbd_direct(workspace_id: int) -> None:
    """
    Update timestamp in QBD Direct App
    """
    workspace = Workspace.objects.get(id=workspace_id)

    payload = {
        'data': {
            'org_id': workspace.org_id,
            'reimbursable_last_synced_at': workspace.reimbursable_last_synced_at.isoformat() if workspace.reimbursable_last_synced_at else None,
            'ccc_last_synced_at': workspace.ccc_last_synced_at.isoformat() if workspace.ccc_last_synced_at else None
        },
        'action': 'UPDATE_LAST_SYNCED_TIMESTAMP'
    }

    api_url = '{}/workspaces/webhook_callback/'.format(settings.QBD_DIRECT_API_URL)

    try:
        logger.info('Posting Timestamp Update to QBD Connector with payload: {}'.format(payload))
        fyle_creds = FyleCredential.objects.filter(workspace_id=workspace.id).first()

        if fyle_creds:
            refresh_token = fyle_creds.refresh_token
            post_request(url=api_url, body=json.dumps(payload), refresh_token=refresh_token)
        else:
            raise Exception('Auth Token not present for workspace id {}'.format(workspace.id))
    except Exception as e:
        logger.error("Failed to sync timestamp to QBD Connector: {}".format(e))
