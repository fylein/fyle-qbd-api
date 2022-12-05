

from typing import List
from apps.fyle.models import Expense
from apps.qbd.models import (
    Bill, BillLineitem,
    CreditCardPurchase, CreditCardPurchaseLineitem
)
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
        'date': bill.date.strftime('%Y-%m-%d'),
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
                'date': bill_lineitem.date.strftime('%Y-%m-%d'),
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


def __create_credit_card_purchases_payload(credit_card_purchase: CreditCardPurchase, credit_card_purchase_lineitems: CreditCardPurchaseLineitem):
    """
    Create Credit Card Purchases Payload
    """
    return {
        'row_type': credit_card_purchase.row_type,
        'transaction_id': credit_card_purchase.transaction_id,
        'transaction_type': credit_card_purchase.transaction_type,
        'date': credit_card_purchase.date.strftime('%Y-%m-%d'),
        'account': credit_card_purchase.account,
        'name': credit_card_purchase.name,
        'class': credit_card_purchase.class_name,
        'amount': credit_card_purchase.amount,
        'document_number': credit_card_purchase.document_number,
        'memo': credit_card_purchase.memo,
        'clear': credit_card_purchase.clear,
        'to_print': credit_card_purchase.to_print,
        'name_is_taxable': credit_card_purchase.name_is_taxable,
        'address_1': credit_card_purchase.address_1,
        'address_2': credit_card_purchase.address_2,
        'address_3': credit_card_purchase.address_3,
        'address_4': credit_card_purchase.address_4,
        'address_5': credit_card_purchase.address_5,
        'due_date': credit_card_purchase.due_date,
        'terms': credit_card_purchase.terms,
        'paid': credit_card_purchase.paid,
        'ship_via': credit_card_purchase.ship_via,
        'ship_date': credit_card_purchase.ship_date,
        'year_to_date': credit_card_purchase.year_to_date,
        'wage_base': credit_card_purchase.wage_base,
        'split_lines': [
            {
                'row_type': credit_card_purchase_lineitem.row_type,
                'split_line_id': credit_card_purchase_lineitem.split_line_id,
                'transaction_type': credit_card_purchase_lineitem.transaction_type,
                'date': credit_card_purchase_lineitem.date.strftime('%Y-%m-%d'),
                'account': credit_card_purchase_lineitem.account,
                'name': credit_card_purchase_lineitem.name,
                'class': credit_card_purchase_lineitem.class_name,
                'amount': credit_card_purchase_lineitem.amount,
                'document_number': credit_card_purchase_lineitem.document_number,
                'memo': credit_card_purchase_lineitem.memo,
                'clear': credit_card_purchase_lineitem.clear,
                'quantity': credit_card_purchase_lineitem.quantity,
                'price': credit_card_purchase_lineitem.price,
                'inventory_item': credit_card_purchase_lineitem.inventory_item,
                'payment_method': credit_card_purchase_lineitem.payment_method,
                'taxable': credit_card_purchase_lineitem.taxable,
                'value_adjustment': credit_card_purchase_lineitem.value_adjustment,
                'reimbursable_expense': credit_card_purchase_lineitem.reimbursable_expense,
                'service_date': credit_card_purchase_lineitem.service_date,
                'others_2': credit_card_purchase_lineitem.others_2,
                'others_3': credit_card_purchase_lineitem.others_3,
                'year_to_date': credit_card_purchase_lineitem.year_to_date,
                'wage_base': credit_card_purchase_lineitem.wage_base
            } for credit_card_purchase_lineitem in credit_card_purchase_lineitems
        ]
    }


def generate_all_credit_card_purchases(expenses: List[Expense], accounting_export: AccountingExport, workspace_id: int):
    """
    Create Credit Card Purchases Payload
    """
    all_credit_card_purchases = []

    export_settings = ExportSettings.objects.get(workspace_id=workspace_id)

    expense_group_map = {}

    for expense in expenses:
        expense_group_map[expense.expense_id] = [expense]
        
    for group_id in expense_group_map:
        credit_card_purchase, credit_card_purchase_lineitems = CreditCardPurchase.create_credit_card_purchase(
            expenses=expense_group_map[group_id], 
            workspace_id=workspace_id,
            export_settings=export_settings,
            accounting_export=accounting_export
        )
       
        all_credit_card_purchases.append(
            __create_credit_card_purchases_payload(credit_card_purchase, credit_card_purchase_lineitems)
        )

    return all_credit_card_purchases
