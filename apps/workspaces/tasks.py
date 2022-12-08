from apps.fyle.queue import queue_import_credit_card_expenses, queue_import_reimbursable_expenses
from apps.qbd.queue import (
    queue_create_bills_iif_file,
    queue_create_credit_card_purchases_iif_file,
    queue_create_journals_iif_file
)
from apps.tasks.models import AccountingExport
from apps.fyle.models import Expense

from .models import ExportSettings 


def run_import_export(workspace_id: int):
    """
    Run Processes to Generate IIF File
    
    :param workspace_id: Workspace id
    """
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
