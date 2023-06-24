import pytest

from apps.fyle.tasks import import_reimbursable_expenses, import_credit_card_expenses
from apps.tasks.models import AccountingExport
from apps.fyle.models import Expense

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
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        mocker,api_client, test_connection, 
        create_temp_workspace, add_export_settings
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

    expenses = Expense.objects.filter(workspace_id=workspace_id, fund_source='PERSONAL', exported=False)

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 5
    assert expenses.first().workspace.reimbursable_last_synced_at is not None

    #Export assert
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_BILLS', status='ENQUEUED'
    )

    create_bills_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert expenses.count() == 0
    assert accounting_export.status == 'COMPLETE'
    assert accounting_export.bills.count() == 4

    for bill in accounting_export.bills.all():
        assert bill.workspace_id == workspace_id
        assert bill.accounting_export_id == accounting_export.id
        assert bill.bill_lineitems.count() >= 1

    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace_id = response.data['id']

    url = reverse(
        'export-settings', kwargs={
            'workspace_id': workspace_id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    payload = {
        'reimbursable_expenses_export_type': 'BILL',
        'bank_account_name': 'Accounts Payable',
        'reimbursable_expense_state': 'PAYMENT_PROCESSING',
        'reimbursable_expense_date': 'posted_at',
        'reimbursable_expense_grouped_by': 'REPORT',
        'credit_card_expense_export_type': 'CREDIT_CARD_PURCHASE',
        'credit_card_expense_state': 'PAYMENT_PROCESSING',
        'credit_card_entity_name_preference': 'VENDOR',
        'credit_card_account_name': 'Visa',
        'credit_card_expense_grouped_by': 'EXPENSE',
        'credit_card_expense_date': 'spent_at'
    }

    api_client.post(url, payload)

    export_1, _ = AccountingExport.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_REIMBURSABLE_EXPENSES',
        defaults={
            'status': 'COMPLETE'
        }
    )

    AccountingExport.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_CREDIT_CARD_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    url = reverse(
        'accounting-exports',
        kwargs={
            'workspace_id': workspace_id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['count'] == 1


