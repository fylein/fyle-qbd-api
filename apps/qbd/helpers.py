

from typing import List
from apps.fyle.models import Expense
from apps.qbd.models import Bill, BillLineitem
from apps.tasks.models import AccountingExport
from apps.workspaces.models import ExportSettings


def __create_bills_payload(bill: Bill, bill_lineitems: BillLineitem):
    """
    Create Bills Payload
    """
    return {
        'row_type': bill.row_type,
        'transaction_id': bill.transaction_id,
        'transaction_type': bill.transaction_type,
        'date': bill.date,
        'account': bill.account,
        'name': bill.name,
        'class': bill.class_name,
        'amount': bill.amount,
        'document_number': bill.document_number,
        'memo': bill.memo,
        'clear': bill.clear,
        'to_print': bill.to_print,
        'address': bill.address,
        'due_date': bill.due_date,
        'terms': bill.terms,
        'split_lines': [
            {
                'row_type': bill_lineitem.row_type,
                'split_line_id': bill_lineitem.split_line_id,
                'transaction_type': bill_lineitem.transaction_type,
                'date': bill_lineitem.date,
                'account': bill_lineitem.account,
                'name': bill_lineitem.name,
                'class': bill_lineitem.class_name,
                'amount': bill_lineitem.amount,
                'document_number': bill_lineitem.document_number,
                'memo': bill_lineitem.memo,
                'clear': bill_lineitem.clear,
                'quantity': bill_lineitem.quantity,
                'reimbursable_expense': bill_lineitem.reimbursable_expense,
                'service_date': bill_lineitem.service_date,
                'others': bill_lineitem.others
            } for bill_lineitem in bill_lineitems
        ]
    }


def generate_all_bills(expenses: List[Expense], accounting_export: AccountingExport, workspace_id: int):
    """
    Create Bills Payload
    """
    all_bills = []

    export_settings = ExportSettings.objects.get(workspace_id=workspace_id)

    if export_settings.reimbursable_expense_grouped_by == 'REPORT':
        expense_group_map = {}

        for expense in expenses:
            if expense.report_id in expense_group_map:
                expense_group_map[expense.report_id].append(expense)
            else:
                expense_group_map[expense.report_id] = [expense]
    else:
        expense_group_map = {}

        for expense in expenses:
            expense_group_map[expense.expense_id] = [expense]
        
    for group_id in expense_group_map:
        bill, bill_lineitems = Bill.create_bill(
            expenses=expense_group_map[group_id], 
            workspace_id=workspace_id,
            export_settings=export_settings,
            accounting_export=accounting_export
        )
       
        all_bills.append(__create_bills_payload(bill, bill_lineitems))

    return all_bills
