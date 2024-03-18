"""
Fixture configuration for all the tests
"""
from datetime import datetime, timezone

from unittest import mock
import pytest

from rest_framework.test import APIClient
from fyle.platform.platform import Platform
from fyle_rest_auth.models import User, AuthToken

from apps.fyle.helpers import get_access_token
from apps.fyle.models import Expense
from apps.workspaces.models import (
    Workspace, FyleCredential,
    ExportSettings, FieldMapping,
    AdvancedSetting
)
from apps.tasks.models import AccountingExport
from apps.mappings.models import QBDMapping
from quickbooks_desktop_api.tests import settings

from .test_fyle.fixtures import fixtures as fyle_fixtures
from .test_mapping.fixtures import fixture as mapping_fixtures


@pytest.fixture
def api_client():
    """
    Fixture required to test views
    """
    return APIClient()


@pytest.fixture()
def test_connection(db):
    """
    Creates a connection with Fyle
    """
    client_id = settings.FYLE_CLIENT_ID
    client_secret = settings.FYLE_CLIENT_SECRET
    token_url = settings.FYLE_TOKEN_URI
    refresh_token = 'Dummy.Refresh.Token'
    server_url = settings.FYLE_BASE_URL

    fyle_connection = Platform(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        server_url=server_url
    )

    access_token = get_access_token(refresh_token)
    fyle_connection.access_token = access_token
    user_profile = fyle_connection.v1beta.spender.my_profile.get()['data']
    user = User(
        password='', last_login=datetime.now(tz=timezone.utc), id=1, email=user_profile['user']['email'],
        user_id=user_profile['user_id'], full_name='', active='t', staff='f', admin='t'
    )

    user.save()

    auth_token = AuthToken(
        id=1,
        refresh_token=refresh_token,
        user=user
    )
    auth_token.save()

    return fyle_connection


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

    patched_5 = mock.patch(
        'fyle_rest_auth.helpers.get_fyle_admin',
        return_value=fyle_fixtures['get_my_profile']
    )
    patched_5.__enter__()


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
            reimbursable_expenses_export_type='BILL' if workspace_id in [1, 2] else 'JOURNAL_ENTRY',
            bank_account_name='Accounts Payable',
            reimbursable_expense_state='PAYMENT_PROCESSING',
            reimbursable_expense_date='current_date' if workspace_id == 1 else 'last_spent_at',
            reimbursable_expense_grouped_by='REPORT' if workspace_id == 1 else 'EXPENSE',
            credit_card_expense_export_type='CREDIT_CARD_PURCHASE' if workspace_id in [1, 2] else 'JOURNAL_ENTRY',
            credit_card_expense_state='PAYMENT_PROCESSING',
            credit_card_account_name='Visa',
            credit_card_entity_name_preference='EMPLOYEE' if workspace_id in [2, 3] else 'VENDOR',
            credit_card_expense_grouped_by='EXPENSE' if workspace_id == 3 else 'REPORT',
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


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_advanced_settings():
    """
    Pytest fixture to add advanced settings to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]

    for workspace_id in workspace_ids:
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
            schedule_is_enabled=True if workspace_id in [1, 2] else False,
            frequency='WEEKLY' if workspace_id in [1, 2] else 'MONTHLY',
            day_of_week='MONDAY' if workspace_id in [1, 2] else 'TUESDAY',
            day_of_month=1 if workspace_id in [1, 2] else 2,
            time_of_day='00:00:00' if workspace_id in [1, 2] else '01:00:00',
            schedule_id=None,
            top_memo_structure=['employee_email', 'purpose'] if workspace_id in [1, 2] else None,
            expense_memo_structure=['employee_email', 'category', 'report_number', 'spent_on', 'expense_link'],
        )


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_expenses():
    """
    Add Expense to a workspace
    """
    expenses = fyle_fixtures['platform_connector_expenses']

    for workspace_id in [1, 2, 3]:
        for expense in expenses:
            expense['id'] = expense['id'] + str(workspace_id)

        Expense.create_expense_objects(expenses, workspace_id)


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_ccc_mapping():
    """
    Add Expense to a workspace
    """
    mappings = mapping_fixtures['create_qbd_mapping']

    for workspace_id in [1, 2, 3]:
        for mapping in mappings:
            QBDMapping.objects.update_or_create(
                    workspace_id= workspace_id,
                    source_value= mapping['value'],
                    attribute_type= mapping['attribute_type'],
                    defaults={
                        'source_id': mapping['source_id'],
                        'destination_value': 'mastercard' if mapping['value'] == 'American Express - 055470' else None
                    }
                )
