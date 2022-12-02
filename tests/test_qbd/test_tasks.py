
import pytest
from apps.fyle.models import Expense
from apps.fyle.tasks import import_reimbursable_expenses
from apps.tasks.models import AccountingExport

from apps.qbd.tasks import create_bills_iif_file

from tests.test_fyle.fixtures import fixtures as fyle_fixtures


@pytest.mark.django_db(databases=['default'])
def test_create_bills_iif_file_report(
        create_temp_workspace, add_accounting_export_bills, 
        add_accounting_export_expenses, add_fyle_credentials, 
        add_export_settings, add_field_mappings, mocker
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
        return_value=fyle_fixtures['reimbursable_expenses']
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


@pytest.mark.django_db(databases=['default'])
def test_create_bills_iif_file_expense(
        create_temp_workspace, add_accounting_export_bills, 
        add_accounting_export_expenses, add_fyle_credentials, 
        add_export_settings, add_field_mappings, mocker
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
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    workspace_id = 3
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_BILLS', status='ENQUEUED'
    )

    create_bills_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert expenses.count() == 0
    assert accounting_export.status == 'COMPLETE'
    assert accounting_export.bills.count() == 5

    for bill in accounting_export.bills.all():
        assert bill.workspace_id == workspace_id
        assert bill.accounting_export_id == accounting_export.id
        assert bill.bill_lineitems.count() == 1

