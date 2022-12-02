"""
Fixture configuration for all the tests
"""
from datetime import datetime, timezone

from unittest import mock
import pytest
from rest_framework.test import APIClient

from apps.workspaces.models import (
    Workspace, FyleCredential,
    ExportSettings, FieldMapping
)
from apps.tasks.models import AccountingExport

from .test_fyle.fixtures import fixtures as fyle_fixtures


@pytest.fixture
def api_client():
    """
    API Client to help test views
    """
    return APIClient()


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(request):
    patched_1 = mock.patch(
        'fyle_rest_auth.authentication.get_fyle_admin',
        return_value=fyle_fixtures['get_my_profile']
    )
    patched_1.__enter__()

    patched_2 = mock.patch(
        'fyle.platform.internals.auth.Auth.update_access_token',
        return_value='asnfalsnkflanskflansfklsan'
    )
    patched_2.__enter__()

    patched_3 = mock.patch(
        'apps.fyle.helpers.post_request',
        return_value={
            'access_token': 'easnfkjo12233.asnfaosnfa.absfjoabsfjk',
            'cluster_domain': 'https://staging.fyle.tech'
        }
    )
    patched_3.__enter__()

    patched_4 = mock.patch(
        'fyle.platform.apis.v1beta.spender.MyProfile.get',
        return_value=fyle_fixtures['get_my_profile']
    )
    patched_4.__enter__()

    def unpatch():
        patched_1.__exit__()
        patched_2.__exit__()
        patched_3.__exit__()
        patched_4.__exit__()

    request.addfinalizer(unpatch)


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
            reimbursable_expense_grouped_by='REPORT' if workspace_id in [1, 2] else 'EXPENSE',
            credit_card_expense_export_type='CREDIT CARD CHARGE',
            credit_card_expense_state='PAYMENT_PROCESSING',
            credit_card_account_name='Credit Card Account Name',
            credit_card_expense_grouped_by='EXPENSE',
            credit_card_expense_date='spent_at'
        )

@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_accounting_export_expenses():
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
def add_field_mappings():
    """
    Pytest fixture to add field mappings to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]

    for workspace_id in workspace_ids:
        FieldMapping.objects.create(
            workspace_id=workspace_id,
            class_type='COST_CENTER' if workspace_id in [1, 2] else 'PROJECT',
            project_type='PROJECT' if workspace_id in [1, 2] else 'COST_CENTER',
        )
