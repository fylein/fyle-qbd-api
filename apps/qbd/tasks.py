
import os

from apps.fyle.models import Expense
from apps.tasks.models import AccountingExport
from apps.utils.iif_generator import QBDIIFGenerator

from .helpers import generate_all_bills


def create_bills_iif_file(workspace_id: int, accounting_export: AccountingExport):
    """
    Create Bills IIF file
    """
    accounting_export.status = 'IN_PROGRESS'
    accounting_export.save()

    file_path = os.path.join('/tmp', 'bills.iif')
    
    expenses = Expense.objects.filter(
        workspace_id=workspace_id,
        exported=False,
        fund_source='PERSONAL'
    ).all()

    if expenses:
        all_bills = generate_all_bills(expenses, accounting_export, workspace_id)
        iif_generator = QBDIIFGenerator(file_path)
        iif_generator.generate_iif_file(all_bills, 'BILL')

        expenses.update(exported=True)
        accounting_export.status = 'COMPLETE'
        accounting_export.save()
