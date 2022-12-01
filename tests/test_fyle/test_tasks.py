import pytest

from apps.fyle.tasks import import_reimbursable_expenses, import_credit_card_expenses
from apps.workspaces.models import Workspace, ExportSettings, FyleCredential
from apps.tasks.models import AccountingExport

from .fixtures import fixtures


@pytest.mark.django_db(databases=['default'])
def test_import_reimbursable_expenses(
        create_temp_workspace, add_accounting_export, 
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

    assert accounting_export.status == 'COMPLETE'


@pytest.mark.django_db(databases=['default'])
def test_import_credit_card_expenses(
        create_temp_workspace, 
        add_accounting_export, 
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

    assert accounting_export.status == 'COMPLETE'
