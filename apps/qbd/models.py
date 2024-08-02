from datetime import datetime
from typing import List

from django.db import models
from django.conf import settings

from apps.fyle.models import Expense
from apps.tasks.models import AccountingExport
from apps.workspaces.models import (
    AdvancedSetting, ExportSettings, FieldMapping, 
    FyleCredential, Workspace
)
from apps.mappings.models import QBDMapping


def get_item_and_account_name(field_mapping: FieldMapping, expense: Expense, workspace_id: int):
    item_type = field_mapping.item_type
    expense_item = None
    expense_category = expense.category

    if item_type.upper() in ['PROJECT', 'COST_CENTER']:
        expense_item = getattr(expense, item_type.lower())
    else:
        custom_properties = getattr(expense, 'custom_properties', {})
        custom_properties = {
            '_'.join(k.lower().split()).replace(' ', '_'): v 
            for k, v in custom_properties.items()
        }
        modified_item_type = item_type = '_'.join(item_type.lower().split()).replace(' ', '_')
        expense_item = custom_properties.get(modified_item_type)
        
    if item_type and expense_item and expense_category:
        item_mapped_account = QBDMapping.objects.filter(
            workspace_id=workspace_id,
            attribute_type=modified_item_type,
            source_value=expense_item).first()
                                                    
        if item_mapped_account:
            return expense_item, item_mapped_account

    return '', expense_category


def get_class_and_project_name(field_mappings: FieldMapping, expense: Expense):
    """
    According to class_type, project_type return the value of project, class field
    class_type can be PROJECT or COST_CENTER or None
    project_type can be PROJECT or COST_CENTER or None
    """
    class_name = None
    project_name = None

    if field_mappings.class_type == 'PROJECT':
        class_name = expense.project

    elif field_mappings.class_type == 'COST_CENTER':
        class_name = expense.cost_center

    if field_mappings.project_type == 'PROJECT':
        project_name = expense.project

    elif field_mappings.project_type == 'COST_CENTER':
        project_name = expense.cost_center

    return class_name, project_name


def get_transaction_date(expenses: List[Expense], date_preference: str) -> str:
    """
    Returns date based on date_preference
    :param expenses: List of expenses
    :param date_preference: Date preference last_spent_at, created_at or spent_at
    """
    if date_preference == 'last_spent_at':
        latest_expense = sorted(expenses, key=lambda expense: expense.spent_at, reverse=True)[0]

        return latest_expense.spent_at

    elif date_preference == 'spent_at':
        return expenses[0].spent_at

    elif date_preference == 'posted_at' and expenses[0].posted_at != None:
        return expenses[0].posted_at

    return datetime.now()


def get_expense_purpose(workspace_id: str, expense: Expense) -> str:
    """
    Get Expense Purpose
    :param workspace_id: Workspace ID
    :param expense: Expense object
    """
    advanced_settings = AdvancedSetting.objects.get(workspace_id=workspace_id)

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    org_id = fyle_credentials.workspace.org_id

    expense_memo_structure = advanced_settings.expense_memo_structure

    details = {
        'employee_name': expense.employee_name,
        'employee_email': expense.employee_email,
        'merchant': '{0}'.format(expense.vendor) if expense.vendor else '',
        'category': '{0}'.format(expense.category) if expense.category else '',
        'purpose': '{0}'.format(expense.purpose) if expense.purpose else '',
        'report_number': '{0}'.format(expense.claim_number),
        'spent_on': '{0}'.format(expense.spent_at.date()) if expense.spent_at else '',
        'expense_link': '{0}/app/admin/#/view_expense/{1}/?org_id={2}'.format(
            settings.FYLE_APP_URL, expense.expense_id, org_id
        )
    }

    memo = ''

    for index, field in enumerate(expense_memo_structure):
        if field in details and details[field]:
            memo = memo + details[field]
            if index + 1 != len(expense_memo_structure):
                if memo:
                    memo = f'{memo} - '

    return memo


def get_top_purpose(workspace_id: str, expense: Expense, default: str) -> str:
    """
    Get Expense Purpose
    :param workspace_id: Workspace ID
    :param expense: Expense object
    """
    advanced_settings = AdvancedSetting.objects.get(workspace_id=workspace_id)

    top_memo_structure = advanced_settings.top_memo_structure

    if not top_memo_structure:
        return default

    details = {
        'employee_name': expense.employee_name,
        'employee_email': expense.employee_email,
        'purpose': f'{expense.purpose}' if expense.purpose else '',
        'merchant': f'{expense.vendor}' if expense.vendor else ''
    }

    memo = ''

    for index, field in enumerate(top_memo_structure):
        if field in details:
            memo = memo + details[field]
            if index + 1 != len(top_memo_structure):
                memo = f'{memo} - '

    return memo


def get_corporate_card_name(corporate_card_id: str, workspace_id: int, export_settings: ExportSettings):
    corporate_card_name = export_settings.credit_card_account_name

    qbd_mapping = QBDMapping.objects.filter(workspace_id=workspace_id, source_id=corporate_card_id)

    if len(qbd_mapping) > 0 and qbd_mapping[0].destination_value:
        corporate_card_name = qbd_mapping[0].destination_value

    return corporate_card_name



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
    memo = models.TextField(null=True, default='')
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
            date=get_transaction_date(expenses, export_settings.reimbursable_expense_date),
            account=export_settings.bank_account_name,
            name=expenses[0].employee_name,
            class_name='',
            amount=sum([expense.amount for expense in expenses]) * -1,
            memo=get_top_purpose(workspace_id=workspace_id,
                expense=expenses[0],
                default=f'Reimbursable Expenses by {expenses[0].employee_email}'
            ),
            accounting_export=accounting_export,
            workspace_id=workspace_id
        )

        line_items = BillLineitem.create_bill_lineitems(expenses, bill, workspace_id, export_settings)
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
    memo = models.TextField(null=True, default='')
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
    def create_bill_lineitems(expenses: List[Expense], bill: Bill, workspace_id: int, export_settings: ExportSettings):
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
            class_name, project_name = get_class_and_project_name(
                field_mappings, expense
            )

            lineitem = BillLineitem.objects.create(
                transaction_type='BILL',
                date=get_transaction_date(expenses, export_settings.reimbursable_expense_date),
                account=export_settings.mileage_account_name if expense.category == 'Mileage' and \
                    export_settings.mileage_account_name else expense.category,
                name=project_name,
                class_name=class_name,
                amount=expense.amount,
                memo=get_expense_purpose(workspace_id, expense),
                reimbursable_expense='Yes',
                bill=bill,
                workspace_id=workspace_id,
                expense=expense
            )

            lineitems.append(lineitem)

        return lineitems


class CreditCardPurchase(models.Model):
    """
    Credit Card Purchase Table Model Class

    Example Data ->
    row_type: 'TRNS'
    transaction_id: ''
    transaction_type: 'CREDIT CARD'
    date: '2021-04-26'
    account: 'Visa'
    name: 'Amazon'
    class: ''
    amount: 1284.22
    document_number: ''
    memo: 'Credit Card Expenses by Shwetabh'
    clear: ''
    to_print: ''
    name_is_taxable: ''
    address_1: '23/11 North Los Robles, Pasadena, California'
    address_2: ''
    address_3: ''
    address_4: ''
    address_5: ''
    due_date: ''
    terms: ''
    paid: ''
    ship_via: ''
    ship_date: ''
    year_to_date: ''
    wage_base: ''
    """
    row_type = models.CharField(max_length=255, default='TRNS')
    transaction_id = models.CharField(max_length=255, default='')
    transaction_type = models.CharField(max_length=255)
    date = models.DateTimeField()
    account = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(help_text='Credit Card amount')
    document_number = models.CharField(max_length=255, null=True, default='')
    memo = models.TextField(null=True, default='')
    clear = models.CharField(max_length=255, default='')
    to_print = models.CharField(max_length=255, default='')
    name_is_taxable = models.CharField(max_length=255, default='')
    address_1 = models.CharField(max_length=255, default='')
    address_2 = models.CharField(max_length=255, default='')
    address_3 = models.CharField(max_length=255, default='')
    address_4 = models.CharField(max_length=255, default='')
    address_5 = models.CharField(max_length=255, default='')
    due_date = models.CharField(max_length=255, default='')
    terms = models.CharField(max_length=255, default='')
    paid = models.CharField(max_length=255, default='')
    ship_via = models.CharField(max_length=255, default='')
    ship_date = models.CharField(max_length=255, default='')
    year_to_date = models.CharField(max_length=255, default='')
    wage_base = models.CharField(max_length=255, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accounting_export = models.ForeignKey(
        AccountingExport, on_delete=models.PROTECT, related_name='credit_card_purchases'
    )

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='credit_card_purchases'
    )

    class Meta:
        db_table = 'credit_card_purchases'

    @staticmethod
    def create_credit_card_purchase(
        expenses: List[Expense],
        export_settings: ExportSettings,
        accounting_export: AccountingExport,
        workspace_id: int

    ):
        """
        Create credit card purchase object
        :param expenses: expense object
        :param export_settings: export settings object
        :param accounting_export: accounting export object
        :param workspace_id: workspace id
        :return: credit card purchase object
        """
        name = expenses[0].vendor if expenses[0].vendor else 'Credit Card Misc'

        date_preference = export_settings.credit_card_expense_date

        corporate_card_name = get_corporate_card_name(expenses[0].corporate_card_id, workspace_id, export_settings)

        if export_settings.credit_card_entity_name_preference == 'EMPLOYEE':
            name = expenses[0].employee_name

        credit_card_purchase = CreditCardPurchase.objects.create(
            transaction_type='CREDIT CARD' if expenses[0].amount > 0 else 'CCARD REFUND',
            date=get_transaction_date(expenses, date_preference),
            account=corporate_card_name,
            name=name,
            class_name='',
            amount=sum([expense.amount for expense in expenses]) * -1,
            memo=get_top_purpose(
                workspace_id=workspace_id,
                expense=expenses[0],
                default=f'Credit Card Expenses by {expenses[0].employee_email}'
            ),
            accounting_export=accounting_export,
            workspace_id=workspace_id
        )
        
        line_items = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(
            expenses, credit_card_purchase, workspace_id)
        return credit_card_purchase, line_items


class CreditCardPurchaseLineitem(models.Model):
    """
    Credit Card Purchase Lineitem Table Model Class

    Example Data ->
    row_type: 'SPL'
    split_line_id: ''
    transaction_type: 'CREDIT CARD'
    date: '2021-04-26'
    account: 'Food'
    name: 'Delloite'
    class: 'Awesome'
    amount: 1284.22
    document_number: ''
    memo: 'Expense on Category - Food'
    clear: ''
    quantity: ''
    price: ''
    inventory_item: ''
    payment_method: ''
    taxable: ''
    value_adjustment: ''
    reimbursable_expense: 'No'
    service_date: ''
    others_2: ''
    others_3: ''
    year_to_date: ''
    wage_base: ''
    """
    row_type = models.CharField(max_length=255, default='SPL')
    split_line_id = models.CharField(max_length=255, default='')
    transaction_type = models.CharField(max_length=255)
    date = models.DateTimeField()
    account = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    class_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(help_text='Credit Card amount')
    document_number = models.CharField(max_length=255, null=True, default='')
    memo = models.TextField(null=True, default='')
    clear = models.CharField(max_length=255, default='')
    quantity = models.CharField(max_length=255, default='')
    price = models.CharField(max_length=255, default='')
    inventory_item = models.CharField(max_length=255, default='')
    payment_method = models.CharField(max_length=255, default='')
    taxable = models.CharField(max_length=255, default='')
    value_adjustment = models.CharField(max_length=255, default='')
    reimbursable_expense = models.CharField(max_length=255)
    service_date = models.CharField(max_length=255, default='')
    others_2 = models.CharField(max_length=255, default='')
    others_3 = models.CharField(max_length=255, default='')
    year_to_date = models.CharField(max_length=255, default='')
    wage_base = models.CharField(max_length=255, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    credit_card_purchase = models.ForeignKey(
        CreditCardPurchase, on_delete=models.PROTECT, related_name='lineitems'
    )
    expense = models.ForeignKey(
        Expense, on_delete=models.PROTECT, related_name='credit_card_purchase_lineitems', null=True
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='credit_card_purchase_lineitems'
    )

    class Meta:
        db_table = 'credit_card_purchase_lineitems'
    
    @staticmethod
    def create_credit_card_purchase_lineitems(
        expenses: List[Expense], credit_card_purchase: CreditCardPurchase, workspace_id: int
    ):
        """
        Create Credit Card Purchase Lineitems
        :param expenses: List of expenses
        :param credit_card_purchase: Credit Card Purchase
        :param workspace_id: Workspace Id
        :return: None
        """
        field_mappings: FieldMapping = FieldMapping.objects.get(workspace_id=workspace_id)
        export_settings: ExportSettings = ExportSettings.objects.get(workspace_id=workspace_id)

        lineitems = []
        for expense in expenses:
            class_name, project_name = get_class_and_project_name(
                field_mappings, expense
            )

            inv_item, account = get_item_and_account_name(
                field_mappings, expense, workspace_id
            )

            lineitem = CreditCardPurchaseLineitem.objects.create(
                transaction_type='CREDIT CARD' if expense.amount > 0 else 'CCARD REFUND',
                date=get_transaction_date(expenses, date_preference=export_settings.credit_card_expense_date),
                account=account,
                name=project_name,
                class_name=class_name,
                amount=expense.amount,
                memo=get_expense_purpose(workspace_id, expense),
                reimbursable_expense='No',
                credit_card_purchase=credit_card_purchase,
                expense=expense,
                workspace_id=workspace_id,
                inventory_item=inv_item
            )

            lineitems.append(lineitem)

        return lineitems


class Journal(models.Model):
    """
    Journal Table Model Class
    
    Example Data ->
    'row_type': 'TRNS',
    'transaction_id': '',
    'transaction_type': 'GENERAL JOURNAL',
    'date': '2021-04-26',
    'account': 'Visa',
    'name': 'Amazon',
    'class': '',
    'amount': 1284.22,
    'document_number': '',
    'memo': 'Credit Card Expenses by Shwetabh',
    """
    row_type = models.CharField(max_length=255, default='TRNS')
    transaction_id = models.CharField(max_length=255, default='')
    transaction_type = models.CharField(max_length=255)
    date = models.DateTimeField()
    account = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    class_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(help_text='Journal amount')
    document_number = models.CharField(max_length=255, null=True, default='')
    memo = models.TextField(null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='journals'
    )
    accounting_export = models.ForeignKey(
        AccountingExport, on_delete=models.PROTECT, related_name='journals', null=True
    )

    class Meta:
        db_table = 'journals'

    @staticmethod
    def create_journal(
        expenses: List[Expense],
        fund_source: str,
        export_settings: ExportSettings,
        accounting_export: AccountingExport,
        workspace_id: int
    ):
        """
        Create Journals
        :param expenses: List of expenses
        :param fund_source: Fund Source
        :param export_settings: Export Settings
        :param accounting_export: Accounting Export
        :param workspace_id: Workspace Id
        """
        name = expenses[0].employee_name

        date_preference = export_settings.reimbursable_expense_date

        if fund_source == 'CCC':
            if export_settings.credit_card_entity_name_preference == 'EMPLOYEE':
                name = expenses[0].employee_name
            else:
                name = expenses[0].vendor if expenses[0].vendor else 'Credit Card Misc'

            date_preference = export_settings.credit_card_expense_date

        corporate_card_name = get_corporate_card_name(expenses[0].corporate_card_id, workspace_id, export_settings)

        default_memo = f'Credit Card Expenses by {expenses[0].employee_email}' \
            if fund_source == 'CCC' else f'Reimbursable Expenses by {expenses[0].employee_email}'

        journal = Journal.objects.create(
            transaction_type='GENERAL JOURNAL',
            date=get_transaction_date(expenses, date_preference=date_preference),
            account=corporate_card_name if fund_source == 'CCC' else export_settings.bank_account_name,
            name=name,
            amount=sum([expense.amount for expense in expenses]) * -1,
            memo=get_top_purpose(
                workspace_id=workspace_id,
                expense=expenses[0],
                default=default_memo
            ),
            accounting_export=accounting_export,
            workspace_id=workspace_id
        )

        lineitems = JournalLineitem.create_journal_lineitems(
            expenses, journal, workspace_id, export_settings, fund_source
        )

        return journal, lineitems


class JournalLineitem(models.Model):
    """
    Journal Lineitem Table Model Class

    Example Data ->
    'row_type': 'SPL',
    'split_line_id': '',
    'transaction_type': 'GENERAL JOURNAL',
    'date': '2021-04-26',
    'account': 'Food',
    'name': 'Delloite',
    'class': 'Awesome',
    'amount': -642.11,
    'document_number': '',
    'memo': 'Amazon.com',
    """
    row_type = models.CharField(max_length=255, default='SPL')
    split_line_id = models.CharField(max_length=255, default='')
    transaction_type = models.CharField(max_length=255)
    date = models.DateTimeField()
    account = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    class_name = models.CharField(max_length=255, null=True)
    amount = models.FloatField(help_text='Journal Lineitem amount')
    document_number = models.CharField(max_length=255, null=True, default='')
    memo = models.TextField(null=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    journal = models.ForeignKey(
        Journal, on_delete=models.PROTECT, related_name='lineitems'
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='journal_lineitems'
    )
    expense = models.ForeignKey(
        Expense, on_delete=models.PROTECT, related_name='journal_lineitems', null=True
    )

    class Meta:
        db_table = 'journal_lineitems'

    @staticmethod
    def create_journal_lineitems(
        expenses: List[Expense], journal: Journal, workspace_id: int, export_settings: ExportSettings, fund_source: str
    ):
        """
        Create Journal Lineitems
        :param expenses: List of expenses
        :param journal: Journal
        :param workspace_id: Workspace Id
        :return: None
        """
        field_mappings: FieldMapping = FieldMapping.objects.get(workspace_id=workspace_id)
        date_preference = export_settings.credit_card_expense_date if fund_source == 'CCC' else export_settings.reimbursable_expense_date

        lineitems = []
        for expense in expenses:
            class_name, _ = get_class_and_project_name(
                field_mappings, expense
            )

            lineitem = JournalLineitem.objects.create(
                transaction_type='GENERAL JOURNAL',
                date=get_transaction_date(expenses, date_preference),
                account=export_settings.mileage_account_name if fund_source != 'CCC' and expense.category == 'Mileage' \
                    and export_settings.mileage_account_name else expense.category,
                name=journal.name,
                class_name=class_name,
                amount=expense.amount,
                memo=get_expense_purpose(workspace_id, expense),
                journal=journal,
                expense=expense,
                workspace_id=workspace_id
            )

            lineitems.append(lineitem)

        return lineitems
