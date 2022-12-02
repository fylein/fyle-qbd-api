from typing import List
from django.db import models
from apps.fyle.models import Expense
from apps.tasks.models import AccountingExport

from apps.workspaces.models import ExportSettings, FieldMapping, Workspace


class Bill(models.Model):
    """
    Bills Table Model Class

    Example Data ->
    row_type: 'TRNS',
    transaction_id: '',
    transaction_type: 'BILL',
    date: '2021-04-26',
    account: 'Accounts Payable',
    name: 'Shwetabh',
    class: 'Awesome',
    amount: 1284.22,
    document_number: '',
    memo: 'Reimbursable Expenses by Shwetabh',
    clear: '',
    to_print: '',
    address: '23/11 North Los Robles, Pasadena, California',
    due_date: '',
    terms': ''
    """
    id = models.AutoField(primary_key=True)
    row_type = models.CharField(max_length=255, default='TRNS')
    transaction_id = models.CharField(max_length=255, default='')
    transaction_type = models.CharField(max_length=255)
    date = models.DateTimeField()
    account = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    amount = models.FloatField(help_text='Bill amount')
    document_number = models.CharField(max_length=255, null=True, default='')
    memo = models.TextField()
    clear = models.CharField(max_length=255, default='')
    to_print = models.CharField(max_length=255, default='')
    address = models.TextField(default='')
    due_date = models.CharField(max_length=255, default='')
    terms = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accounting_export = models.ForeignKey(
        AccountingExport, on_delete=models.PROTECT, related_name='bills'
    )

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='bills'
    )

    class Meta:
        db_table = 'bills'
    
    @staticmethod
    def create_bill(
        expenses: List[Expense],
        export_settings: ExportSettings,
        accounting_export: AccountingExport,
        workspace_id: int
    ):
        """
        Create bill object
        :param bill: bill data
        :param accounting_export: accounting export object
        :param workspace_id: workspace id
        :return: bill object
        """
        bill = Bill.objects.create(
            transaction_type='BILL',
            date=expenses[0].spent_at,
            account=export_settings.bank_account_name,
            name=expenses[0].employee_name,
            class_name='',
            amount=sum([expense.amount for expense in expenses]),
            memo='Reimbursable Expenses by {}'.format(expenses[0].employee_email),
            accounting_export=accounting_export,
            workspace_id=workspace_id
        )

        line_items = BillLineitem.create_bill_lineitems(expenses, bill, workspace_id)
        return bill, line_items


class BillLineitem(models.Model):
    """
    Bill Lineitem Table Model Class

    Example Data ->
    row_type: 'SPL',
    split_line_id: '',
    transaction_type: 'BILL',
    date: '2021-04-26',
    accounts: 'Food',
    name: 'Delloite',
    class: 'Awesome',
    amount: 1284.22,
    document_number: '',
    memo: 'Expense on Category - Food',
    clear: '',
    quantity: '',
    reimbursable_expense: 'Yes',
    service_date: '',
    others: ''
    """
    row_type = models.CharField(max_length=255, default='SPL')
    split_line_id = models.CharField(max_length=255, default='')
    transaction_type = models.CharField(max_length=255)
    date = models.DateTimeField()
    account = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    class_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(help_text='Bill amount')
    document_number = models.CharField(max_length=255, null=True, default='')
    memo = models.TextField()
    clear = models.CharField(max_length=255, default='')
    quantity = models.CharField(max_length=255, default='')
    reimbursable_expense = models.CharField(max_length=255)
    service_date = models.CharField(max_length=255, default='')
    others = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bill = models.ForeignKey(
        Bill, on_delete=models.PROTECT, related_name='bill_lineitems'
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='bill_lineitems'
    )
    expense = models.OneToOneField(
        Expense, on_delete=models.PROTECT, related_name='bill_lineitems', null=True
    )

    class Meta:
        db_table = 'bill_lineitems'
    
    @staticmethod
    def create_bill_lineitems(expenses: List[Expense], bill: Bill, workspace_id: int):
        """
        Create bill lineitem object
        :param bill_lineitem: bill lineitem data
        :param bill: bill object
        :param workspace_id: workspace id
        :return: bill lineitem object
        """
        field_mappings: FieldMapping = FieldMapping.objects.get(workspace_id=workspace_id)

        lineitems = []
        for expense in expenses:
            class_name = expense.project if field_mappings.class_type == 'PROJECT' else expense.cost_center
            project_name = expense.project if field_mappings.project_type == 'PROJECT' else expense.cost_center

            lineitem = BillLineitem.objects.create(
                transaction_type='BILL',
                date=expense.spent_at,
                account=expense.category,
                name=project_name,
                class_name=class_name,
                amount=expense.amount,
                memo='Expense on Category - {}'.format(expense.category),
                reimbursable_expense='Yes',
                bill=bill,
                workspace_id=workspace_id,
                expense=expense
            )

            lineitems.append(lineitem)

        return lineitems
