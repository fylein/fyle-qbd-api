import pytest
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework import status

from apps.fyle.tasks import (
    import_reimbursable_expenses,
    import_credit_card_expenses,
    update_non_exported_expenses
)
from apps.tasks.models import AccountingExport
from apps.fyle.models import Expense
from apps.workspaces.models import Workspace, ExportSettings, AdvancedSetting, FieldMapping
from apps.qbd.models import Journal
from .fixtures import fixtures


@pytest.mark.django_db(databases=['default'])
def test_import_reimbursable_expenses(
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fixtures['reimbursable_expenses']
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')

    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_reimbursable_expenses(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, fund_source='PERSONAL', exported=False)

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 5
    assert expenses.first().workspace.reimbursable_last_synced_at is not None



@pytest.mark.django_db(databases=['default'])
def test_import_reimbursable_expenses_fatal(
        create_temp_workspace, add_accounting_export_expenses, mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fixtures['reimbursable_expenses']
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    import_reimbursable_expenses(workspace_id, accounting_export)

    assert accounting_export.status == 'FATAL'


@pytest.mark.django_db(databases=['default'])
def test_import_reimbursable_expenses_fail(
        create_temp_workspace, add_accounting_export_expenses, add_export_settings, 
        mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fixtures['reimbursable_expenses']
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    import_reimbursable_expenses(workspace_id, accounting_export)

    assert accounting_export.status == 'FAILED'


@pytest.mark.django_db(databases=['default'])
def test_import_credit_card_expenses(
        create_temp_workspace, 
        add_accounting_export_expenses, 
        add_fyle_credentials, 
        add_export_settings, 
        mocker
    ):
    """
    Test import credit card expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fixtures['credit_card_expenses']
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()
    import_credit_card_expenses(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, fund_source='CCC', exported=False)

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 5
    assert expenses.first().workspace.ccc_last_synced_at is not None


@pytest.mark.django_db(databases=['default'])
def test_import_credit_card_expenses_failed(
        create_temp_workspace, 
        add_accounting_export_expenses, 
        add_export_settings, 
        mocker
    ):
    """
    Test import credit card expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fixtures['credit_card_expenses']
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    import_credit_card_expenses(workspace_id, accounting_export)

    assert accounting_export.status == 'FAILED'


@pytest.mark.django_db(databases=['default'])
def test_import_credit_card_expenses_fatal(
        create_temp_workspace, 
        add_accounting_export_expenses,
        mocker
    ):
    """
    Test import credit card expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fixtures['credit_card_expenses']
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    import_credit_card_expenses(workspace_id, accounting_export)

    assert accounting_export.status == 'FATAL'

@pytest.mark.django_db(databases=['default'])
def test_support_post_date_integration(
        create_temp_workspace, 
        add_accounting_export_expenses, 
        add_fyle_credentials, 
        add_export_settings, 
        mocker
    ):
    workspace_id = 1
    payload = fixtures['platform_connector_expenses']
    expense_id = fixtures['platform_connector_expenses'][0]['id']
    Expense.create_expense_objects(payload, workspace_id)

    expense_objects = Expense.objects.get(expense_id=expense_id)
    assert expense_objects.posted_at.strftime("%m/%d/%Y") == '05/06/2022'

    export_settings = ExportSettings.objects.get(workspace_id=workspace_id)
    export_settings.credit_card_expense_date = 'posted_at'
    export_settings.save()

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    AdvancedSetting.objects.create(
            workspace_id=workspace_id,
            emails_selected=[
                {
                    'name': 'Shwetabh Kumar',
                    'email': 'shwetabh.kumar@fylehq.com'
                },
                {
                    'name': 'Netra Ballabh',
                    'email': 'nilesh.p@fylehq.com'
                },
            ],
            schedule_is_enabled=True,
            frequency='WEEKLY' ,
            day_of_week='MONDAY' ,
            day_of_month=1 ,
            time_of_day='00:00:00' ,
            schedule_id=None,
            top_memo_structure=['employee_email', 'purpose'],
            expense_memo_structure=['employee_email', 'category', 'report_number', 'spent_on', 'expense_link'],
        )
    FieldMapping.objects.create(
            workspace_id=workspace_id,
            class_type='COST_CENTER' ,
            project_type='PROJECT' ,
        )
    journals = Journal.create_journal([expense_objects], 'CCC', export_settings, accounting_export, workspace_id)

    assert journals[0].date.strftime("%m/%d/%Y") == '05/06/2022'


def test_update_non_exported_expenses(db, create_temp_workspace, mocker, api_client):
    expense = fixtures['raw_expense']
    default_raw_expense = fixtures['default_raw_expense']
    org_id = expense['org_id']
    payload = {
        "resource": "EXPENSE",
        "action": 'UPDATED_AFTER_APPROVAL',
        "data": expense,
        "reason": 'expense update testing',
    }

    expense_created, _ = Expense.objects.update_or_create(
        org_id=org_id,
        expense_id='txhJLOSKs1iN',
        workspace_id=1,
        defaults=default_raw_expense
    )
    expense_created.exported = False
    expense_created.save()

    workspace = Workspace.objects.filter(id=1).first()
    workspace.org_id = org_id
    workspace.save()

    assert expense_created.category == 'Old Category'

    update_non_exported_expenses(payload['data'])

    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'ABN Withholding'

    expense.exported = True
    expense.category = 'Old Category'
    expense.save()

    update_non_exported_expenses(payload['data'])
    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'Old Category'

    try:
        update_non_exported_expenses(payload['data'])
    except ValidationError as e:
        assert e.detail[0] == 'Workspace mismatch'

#     uncomment this while using the webhook callback for edit expense
#     url = reverse('webhook-callback', kwargs={'workspace_id': 1})
#     response = api_client.post(url, data=payload, format='json')
#     assert response.status_code == status.HTTP_200_OK

#     url = reverse('webhook-callback', kwargs={'workspace_id': 2})
#     response = api_client.post(url, data=payload, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
