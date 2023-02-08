from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.postgres.fields import ArrayField

User = get_user_model()


ONBOARDING_STATE_CHOICES = (
    ('EXPORT_SETTINGS', 'EXPORT_SETTINGS'),
    ('FIELD_MAPPINGS', 'FIELD_MAPPINGS'),
    ('ADVANCED_SETTINGS', 'ADVANCED_SETTINGS'),
    ('COMPLETE', 'COMPLETE')
)


def get_default_onboarding_state():
    return 'EXPORT_SETTINGS'


class Workspace(models.Model):
    """
    Workspace model
    """
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    name = models.CharField(max_length=255, help_text='Name of the workspace')
    user = models.ManyToManyField(User, help_text='Reference to users table')
    org_id = models.CharField(max_length=255, help_text='org id', unique=True)
    currency = models.CharField(max_length=255, help_text='fyle currency', null=True)
    
    reimbursable_last_synced_at = models.DateTimeField(
        help_text='Datetime when reimbursable expenses were pulled last', 
        null=True
    )
    ccc_last_synced_at = models.DateTimeField(
        help_text='Datetime when credit card expenses were pulled last', 
        null=True
    )

    onboarding_state = models.CharField(
        max_length=50, choices=ONBOARDING_STATE_CHOICES, default=get_default_onboarding_state,
        help_text='Onboarding status of the workspace', null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'workspaces'


class FyleCredential(models.Model):
    """
    Table to store Fyle credentials
    """
    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores Fyle refresh token')
    cluster_domain = models.CharField(max_length=255, help_text='Cluster Domain', null=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'fyle_credentials'


# Reimbursable Expense Choices
REIMBURSABLE_EXPENSE_EXPORT_TYPE_CHOICES = (
    ('BILL', 'BILL'),
    ('JOURNAL_ENTRY', 'JOURNAL_ENTRY')
)

REIMBURSABLE_EXPENSE_STATE_CHOICES = (
    ('PAYMENT_PROCESSING', 'PAYMENT_PROCESSING'),
    ('PAID', 'PAID')
)

REIMBURSABLE_EXPENSES_GROUPED_BY_CHOICES = (
    ('REPORT', 'report_id'),
    ('EXPENSE', 'expense_id')
)

REIMBURSABLE_EXPENSES_DATE_TYPE_CHOICES = (
    ('last_spent_at', 'last_spent_at'),
    ('created_at', 'created_at'),
    ('spent_at', 'spent_at')
)

# Credit Card Expense Choices
CREDIT_CARD_EXPENSE_EXPORT_TYPE_CHOICES = (
    ('JOURNAL_ENTRY', 'JOURNAL_ENTRY'),
    ('CREDIT_CARD_PURCHASE', 'CREDIT_CARD_PURCHASE')
)

CREDIT_CARD_EXPENSE_STATE_CHOICES = (
    ('APPROVED', 'APPROVED'),
    ('PAYMENT_PROCESSING', 'PAYMENT_PROCESSING'),
    ('PAID', 'PAID')
)

CREDIT_CARD_EXPENSES_GROUPED_BY_CHOICES = (
    ('REPORT', 'report_id'),
    ('EXPENSE', 'expense_id')
)

CREDIT_CARD_EXPENSES_DATE_TYPE_CHOICES = (
    ('last_spent_at', 'last_spent_at'),
    ('spent_at', 'spent_at'),
    ('created_at', 'created_at')
)

CREDIT_CARD_EXPENSES_ENTITY_NAME_CHOICES = (
    ('EMPLOYEE', 'EMPLOYEE'),
    ('VENDOR', 'VENDOR')
)


class ExportSettings(models.Model):
    """
    Table to store export settings
    id: Primary key
    workspace_id: Foreign Key to Workspace model
    created_at: Created at datetime
    updated_at: Updated at datetime

    reimbursable_expenses_export_type: Export type for reimbursable expenses
    bank_account_name: Bank account name
    reimbursable_expense_state: Reimbursable expense state
    reimbursable_expense_date: Reimbursable expense date
    reimbursable_expense_grouped_by: Reimbursable expense grouped by
    
    credit_card_expense_export_type: Export type for credit card expenses
    credit_card_expense_state: Credit card expense state
    credit_card_account_name: Credit card account name
    credit_card_expense_grouped_by: Credit card expense grouped by
    credit_card_expense_date: Credit card expense date
    """
    id = models.AutoField(primary_key=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    # Reimbursable Expenses Export Settings
    reimbursable_expenses_export_type = models.CharField(
        max_length=255, 
        choices=REIMBURSABLE_EXPENSE_EXPORT_TYPE_CHOICES,
        null=True
    )
    bank_account_name = models.CharField(
        max_length=255, help_text='Bank account name', 
        null=True
    )
    reimbursable_expense_state = models.CharField(
        max_length=255,
        choices=REIMBURSABLE_EXPENSE_STATE_CHOICES,
        null=True
    )
    reimbursable_expense_date = models.CharField(
        max_length=255,
        choices=REIMBURSABLE_EXPENSES_DATE_TYPE_CHOICES,
        null=True
    )
    reimbursable_expense_grouped_by = models.CharField(
        max_length=255,
        choices=REIMBURSABLE_EXPENSES_GROUPED_BY_CHOICES,
        null=True
    )
    
    # Credit Card Expenses Export Settings
    credit_card_expense_export_type = models.CharField(
        max_length=255,
        choices=CREDIT_CARD_EXPENSE_EXPORT_TYPE_CHOICES,
        null=True
    )
    credit_card_expense_state = models.CharField(
        max_length=255,
        choices=CREDIT_CARD_EXPENSE_STATE_CHOICES,
        null=True
    )
    credit_card_entity_name_preference = models.CharField(
        max_length=255,
        choices=CREDIT_CARD_EXPENSES_ENTITY_NAME_CHOICES,
        null=True
    )
    credit_card_account_name = models.CharField(
        max_length=255, help_text='Credit card account name',
        null=True
    )
    credit_card_expense_grouped_by = models.CharField(
        max_length=255,
        choices=CREDIT_CARD_EXPENSES_GROUPED_BY_CHOICES,
        null=True
    )
    credit_card_expense_date = models.CharField(
        max_length=255,
        choices=CREDIT_CARD_EXPENSES_DATE_TYPE_CHOICES,
        null=True
    )

    class Meta:
        db_table = 'export_settings'


class FieldMapping(models.Model):
    """
    Table to store field mappings
    id: Primary key
    workspace_id: Foreign Key to Workspace model
    created_at: Created at datetime
    updated_at: Updated at datetime

    class_type: Class Mapped to Fyle Field
    project_type: Project Mapped to Fyle Field
    """
    id = models.AutoField(primary_key=True)
    workspace = models.OneToOneField(
        Workspace, 
        on_delete=models.PROTECT, 
        help_text='Reference to Workspace model'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class_type = models.CharField(
        max_length=255, help_text='Class Mapped to Fyle Field', null=True)
    project_type = models.CharField(
        max_length=255, help_text='Project Mapped to Fyle Field', null=True)

    class Meta:
        db_table = 'field_mapping'


FREQUENCY_CHOICES = (
    ('DAILY', 'DAILY'),
    ('WEEKLY', 'WEEKLY'),
    ('MONTHLY', 'MONTHLY')
)

DAY_OF_MONTH_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
    ('31', '31')
)


DAY_OF_WEEK_CHOICES = (
    ('MONDAY', 'MONDAY'),
    ('TUESDAY', 'TUESDAY'),
    ('WEDNESDAY', 'WEDNESDAY'),
    ('THURSDAY', 'THURSDAY'),
    ('FRIDAY', 'FRIDAY'),
    ('SATURDAY', 'SATURDAY'),
    ('SUNDAY', 'SUNDAY')
)

class AdvancedSetting(models.Model):
    """
    Table to store advanced settings
    id: Primary key
    workspace_id: Foreign Key to Workspace model
    created_at: Created at datetime
    updated_at: Updated at datetime

    expense_memo_structure: Array of fields in memo
    schedule_is_enabled: Boolean to check if schedule is enabled

    frequency: Frequency of schedule

    day_of_month: Day of month for schedule
    day_of_week: Day of week for schedule
    time_of_day: Time of day for schedule
    schedule_id: Schedule id
    emails_selected: Array of emails_selected

    """
    id = models.AutoField(primary_key=True)
    workspace = models.OneToOneField(
        Workspace, 
        on_delete=models.PROTECT, 
        help_text='Reference to Workspace model'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    top_memo_structure = ArrayField(
        models.CharField(max_length=255), help_text='Array of fields in memo', null=True
    )
    expense_memo_structure = ArrayField(
        models.CharField(max_length=255), help_text='Array of fields in memo', null=True
    )
    schedule_is_enabled = models.BooleanField(help_text='Boolean to check if schedule is enabled', default=False)
    frequency = models.CharField(
        max_length=255, choices=FREQUENCY_CHOICES, help_text='Frequency for schedule', null=True)

    day_of_month = models.CharField(
        max_length=5, choices=DAY_OF_MONTH_CHOICES, help_text='Day of month for schedule', null=True
    )
    day_of_week = models.CharField(
        max_length=10, choices=DAY_OF_WEEK_CHOICES, help_text='Day of week for schedule', null=True
    )

    time_of_day = models.TimeField(help_text='Time of day for schedule', null=True)

    schedule_id = models.CharField(max_length=255, help_text='Schedule id', null=True)
    emails_selected = models.JSONField(
        default=list, help_text='Emails Selected For Email Notification',  null=True)

    class Meta:
        db_table = 'advanced_settings'
