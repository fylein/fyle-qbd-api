import pytest
from apps.workspaces.tasks import run_import_export

from apps.tasks.models import AccountingExport

from tests.test_fyle.fixtures import fixtures as fyle_fixtures

from django_q.models import OrmQ


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_run_import_export_bill_ccp(
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        add_field_mappings, add_advanced_settings,
        mocker
    ):
    """
    Test run import export
    """
    workspace_id = 1
    
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch('apps.fyle.queue.queue_import_reimbursable_expenses')
    mocker.patch('apps.fyle.queue.queue_import_credit_card_expenses')

    accounts_exports = AccountingExport.objects.filter(
        workspace_id=workspace_id,
        type__in=['FETCHING_REIMBURSABLE_EXPENSES', 'FETCHING_CREDIT_CARD_EXPENSES']
    )

    accounts_exports.update(status='COMPLETE')

    run_import_export(workspace_id)

    accounts_exports = AccountingExport.objects.filter(
        workspace_id=workspace_id,
        type__in=['FETCHING_REIMBURSABLE_EXPENSES', 'FETCHING_CREDIT_CARD_EXPENSES']
    )

    tasks = OrmQ.objects.all()

    assert tasks.count() == 2


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_run_import_export_journal_journal(
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        add_field_mappings, add_advanced_settings,
        mocker
    ):
    """
    Test run import export
    """
    workspace_id = 3
    
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch('apps.fyle.queue.queue_import_reimbursable_expenses')
    mocker.patch('apps.fyle.queue.queue_import_credit_card_expenses')

    accounts_exports = AccountingExport.objects.filter(
        workspace_id=workspace_id,
        type__in=['FETCHING_REIMBURSABLE_EXPENSES', 'FETCHING_CREDIT_CARD_EXPENSES']
    )

    accounts_exports.update(status='COMPLETE')

    run_import_export(workspace_id)

    accounts_exports = AccountingExport.objects.filter(
        workspace_id=workspace_id,
        type__in=['FETCHING_REIMBURSABLE_EXPENSES', 'FETCHING_CREDIT_CARD_EXPENSES']
    )

    tasks = OrmQ.objects.all()

    assert tasks.count() == 2
