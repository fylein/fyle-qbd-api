from datetime import datetime, timezone
import pytest

from apps.workspaces.models import Workspace, FyleCredential, ExportSettings
from apps.tasks.models import AccountingExport



@pytest.fixture
@pytest.mark.django_db(databases=['default'])
def create_temp_workspace():
    """
    Pytest fixture to create a temorary workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        Workspace.objects.create(
            id=workspace_id,
            name='Fyle For Testing {}'.format(workspace_id),
            org_id='riseabovehate{}'.format(workspace_id),
            reimbursable_last_synced_at=None,
            ccc_last_synced_at=None,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc)
        )

@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_fyle_credentials():
    """
    Pytest fixture to add fyle credentials to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        FyleCredential.objects.create(
            refresh_token='dummy_refresh_token',
            workspace_id=workspace_id,
            cluster_domain='https://dummy_cluster_domain.com',
        )


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_accounting_export():
    """
    Pytest fixture to add accounting export to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        AccountingExport.objects.update_or_create(
            workspace_id=workspace_id,
            type='FETCHING_REIMBURSABLE_EXPENSES',
            defaults={
                'status': 'IN_PROGRESS'
            }
        )

        AccountingExport.objects.update_or_create(
            workspace_id=workspace_id,
            type='FETCHING_CREDIT_CARD_EXPENSES',
            defaults={
                'status': 'IN_PROGRESS'
            }
        )


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_export_settings():
    """
    Pytest fixture to add export settings to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        ExportSettings.objects.create(
            workspace_id=workspace_id,
            reimbursable_expenses_export_type='BILL',
            bank_account_name='Bank Account Name',
            reimbursable_expense_state='PAYMENT_PROCESSING',
            reimbursable_expense_date='CREATED_AT',
            reimbursable_expense_grouped_by='REPORT',
            credit_card_expense_export_type='CREDIT CARD CHARGE',
            credit_card_expense_state='PAYMENT_PROCESSING',
            credit_card_account_name='Credit Card Account Name',
            credit_card_expense_grouped_by='EXPENSE',
            credit_card_expense_date='spent_at'
        )
