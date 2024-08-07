"""
All Tasks from which involve Fyle APIs

1. Import Reimbursable Expenses from Fyle
2. Import Credit Card Expenses from Fyle
"""
import logging
from typing import Dict
from datetime import datetime
import traceback

from django.db import transaction

from fyle_integrations_platform_connector import PlatformConnector
from fyle.platform.exceptions import RetryException, NoPrivilegeError
from fyle_integrations_platform_connector.apis.expenses import Expenses as FyleExpenses

from apps.tasks.models import AccountingExport
from apps.workspaces.models import Workspace, ExportSettings, FyleCredential

from .models import Expense


logger = logging.getLogger(__name__)


def import_reimbursable_expenses(workspace_id, accounting_export: AccountingExport):
    """
    Import reimbursable expenses from Fyle
    :param accounting_export: Task log object
    :param workspace_id: workspace id
    """
    try:
        # Get export settings to determine Expense State
        export_settings = ExportSettings.objects.get(workspace_id=workspace_id)
        workspace = Workspace.objects.get(pk=workspace_id)
        last_synced_at = workspace.reimbursable_last_synced_at
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)

        expenses = platform.expenses.get(
            source_account_type=['PERSONAL_CASH_ACCOUNT'],
            state=export_settings.reimbursable_expense_state,
            settled_at=last_synced_at if export_settings.reimbursable_expense_state == 'PAYMENT_PROCESSING' else None,
            filter_credit_expenses=True,
            last_paid_at=last_synced_at if export_settings.reimbursable_expense_state == 'PAID' else None
        )

        if expenses:
            workspace.reimbursable_last_synced_at = datetime.now()
            workspace.save()

        with transaction.atomic():
            Expense.create_expense_objects(expenses, workspace_id)

        accounting_export.status = 'COMPLETE'
        accounting_export.detail = None

        accounting_export.save()

    except FyleCredential.DoesNotExist:
        logger.info('Fyle credentials not found %s', workspace_id)
        accounting_export.detail = {
            'message': 'Fyle credentials do not exist in workspace'
        }
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except RetryException:
        logger.info('Fyle Retry Exception occured in workspace_id %s', workspace_id)
        accounting_export.detail = {
            'message': 'Fyle Retry Exception occured'
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()

    except Exception:
        error = traceback.format_exc()
        accounting_export.detail = {
            'error': error
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.detail)


def import_credit_card_expenses(workspace_id, accounting_export: AccountingExport):
    """
    Import credit card expenses from Fyle
    :param accounting_export: Task log object
    :param workspace_id: workspace id
    """
    try:
        # Get export settings to determine Expense State
        export_settings = ExportSettings.objects.get(workspace_id=workspace_id)
        workspace = Workspace.objects.get(pk=workspace_id)
        last_synced_at = workspace.ccc_last_synced_at
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)

        expenses = platform.expenses.get(
            source_account_type=['PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'],
            state=export_settings.credit_card_expense_state,
            settled_at=last_synced_at if export_settings.credit_card_expense_state == 'PAYMENT_PROCESSING' else None,
            approved_at=last_synced_at if export_settings.credit_card_expense_state == 'APPROVED' else None,
            filter_credit_expenses=False,
            last_paid_at=last_synced_at if export_settings.credit_card_expense_state == 'PAID' else None
        )

        if expenses:
            workspace.ccc_last_synced_at = datetime.now()
            workspace.save()

        with transaction.atomic():
            Expense.create_expense_objects(expenses, workspace_id)

        accounting_export.status = 'COMPLETE'
        accounting_export.errors = None

        accounting_export.save()

    except FyleCredential.DoesNotExist:
        logger.info('Fyle credentials not found %s', workspace_id)
        accounting_export.errors = {
            'message': 'Fyle credentials do not exist in workspace'
        }
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except RetryException:
        logger.info('Fyle Retry Exception occured in workspace_id %s', workspace_id)
        accounting_export.detail = {
            'message': 'Fyle Retry Exception occured'
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()

    except NoPrivilegeError:
        logger.info('The user has insufficient privilege error in workspace_id %s', workspace_id)
        accounting_export.errors = {
            'message': 'Fyle No Privilege Error occured'
        }
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except Exception:
        error = traceback.format_exc()
        accounting_export.errors = {
            'error': error
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.errors)


def update_non_exported_expenses(data: Dict) -> None:
    """
    To update expenses not in COMPLETE, IN_PROGRESS state
    """
    org_id = data['org_id']
    expense_id = data['id']
    workspace = Workspace.objects.get(org_id=org_id)
    expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

    if expense and not expense.exported:
        expense_obj = []
        expense_obj.append(data)
        expense_objects = FyleExpenses().construct_expense_object(expense_obj, expense.workspace_id)
        Expense.create_expense_objects(
            expense_objects, expense.workspace_id, skip_update=True
        )
