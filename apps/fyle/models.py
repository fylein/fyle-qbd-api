"""
Fyle Models
"""
import logging
from typing import List, Dict

from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from django.db import models

from apps.workspaces.models import Workspace


logger = logging.getLogger(__name__)
logger.level = logging.INFO



SOURCE_ACCOUNT_MAP = {
    'PERSONAL_CASH_ACCOUNT': 'PERSONAL',
    'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT': 'CCC'
}


class Expense(models.Model):
    """
    Expense
    """
    id = models.AutoField(primary_key=True)
    employee_email = models.EmailField(max_length=255, unique=False, help_text='Email id of the Fyle employee')
    employee_name = models.CharField(max_length=255, null=True, help_text='Name of the Fyle employee')
    category = models.CharField(max_length=255, null=True, blank=True, help_text='Fyle Expense Category')
    sub_category = models.CharField(max_length=255, null=True, blank=True, help_text='Fyle Expense Sub-Category')
    project = models.CharField(max_length=255, null=True, blank=True, help_text='Project')
    expense_id = models.CharField(max_length=255, unique=True, help_text='Expense ID')
    org_id = models.CharField(max_length=255, null=True, help_text='Organization ID')
    expense_number = models.CharField(max_length=255, help_text='Expense Number')
    claim_number = models.CharField(max_length=255, help_text='Claim Number', null=True)
    amount = models.FloatField(help_text='Home Amount')
    currency = models.CharField(max_length=5, help_text='Home Currency')
    foreign_amount = models.FloatField(null=True, help_text='Foreign Amount')
    foreign_currency = models.CharField(null=True, max_length=5, help_text='Foreign Currency')
    settlement_id = models.CharField(max_length=255, help_text='Settlement ID', null=True)
    reimbursable = models.BooleanField(default=False, help_text='Expense reimbursable or not')
    state = models.CharField(max_length=255, help_text='Expense state')
    vendor = models.CharField(max_length=255, null=True, blank=True, help_text='Vendor')
    cost_center = models.CharField(max_length=255, null=True, blank=True, help_text='Fyle Expense Cost Center')
    corporate_card_id = models.CharField(max_length=255, null=True, blank=True, help_text='Corporate Card ID')
    purpose = models.TextField(null=True, blank=True, help_text='Purpose')
    report_id = models.CharField(max_length=255, help_text='Report ID')
    billable = models.BooleanField(default=False, help_text='Expense billable or not')
    file_ids = ArrayField(base_field=models.CharField(max_length=255), null=True, help_text='File IDs')
    spent_at = models.DateTimeField(null=True, help_text='Expense spent at')
    approved_at = models.DateTimeField(null=True, help_text='Expense approved at')
    expense_created_at = models.DateTimeField(help_text='Expense created at')
    expense_updated_at = models.DateTimeField(help_text='Expense created at')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')
    fund_source = models.CharField(max_length=255, help_text='Expense fund source')
    verified_at = models.DateTimeField(help_text='Report verified at', null=True)
    custom_properties = JSONField(null=True)
    tax_amount = models.FloatField(null=True, help_text='Tax Amount')
    tax_group_id = models.CharField(null=True, max_length=255, help_text='Tax Group ID')
    exported = models.BooleanField(default=False, help_text='Expense reimbursable or not')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Workspace reference')


    class Meta:
        db_table = 'expenses'

    @staticmethod
    def create_expense_objects(expenses: List[Dict], workspace_id: int):
        """
        Bulk create expense objects
        """
        expense_objects = []

        for expense in expenses:
            expense_object, _ = Expense.objects.update_or_create(
                expense_id=expense['id'],
                workspace_id=workspace_id,
                defaults={
                    'employee_email': expense['employee_email'],
                    'employee_name': expense['employee_name'],
                    'category': expense['category'],
                    'sub_category': expense['sub_category'],
                    'project': expense['project'],
                    'expense_number': expense['expense_number'],
                    'org_id': expense['org_id'],
                    'claim_number': expense['claim_number'],
                    'amount': expense['amount'],
                    'currency': expense['currency'],
                    'foreign_amount': expense['foreign_amount'],
                    'foreign_currency': expense['foreign_currency'],
                    'settlement_id': expense['settlement_id'],
                    'reimbursable': expense['reimbursable'],
                    'state': expense['state'],
                    'vendor': expense['vendor'][:250] if expense['vendor'] else None,
                    'cost_center': expense['cost_center'],
                    'corporate_card_id': expense['corporate_card_id'],
                    'purpose': expense['purpose'],
                    'report_id': expense['report_id'],
                    'file_ids': expense['file_ids'],
                    'spent_at': expense['spent_at'],
                    'approved_at': expense['approved_at'],
                    'expense_created_at': expense['expense_created_at'],
                    'expense_updated_at': expense['expense_updated_at'],
                    'fund_source': SOURCE_ACCOUNT_MAP[expense['source_account_type']],
                    'verified_at': expense['verified_at'],
                    'custom_properties': expense['custom_properties'],
                    'tax_amount': expense['tax_amount'], 
                    'tax_group_id': expense['tax_group_id'],
                    'billable': expense['billable'] if expense['billable'] else False
                }
            )
            print(expense_object, expense_object.exported)
            expense_objects.append(expense_object)

        return expense_objects


class Reimbursement:
    """
    Creating a dummy class to be able to user
    fyle_integrations_platform_connector correctly
    """
    pass
