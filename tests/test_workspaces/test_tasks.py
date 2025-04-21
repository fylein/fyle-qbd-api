import pytest

from rest_framework.exceptions import ValidationError

from apps.fyle.models import Expense
from apps.workspaces.models import Workspace, FyleCredential
from apps.workspaces.tasks import (
    async_update_fyle_credentials,
    async_handle_webhook_callback,
    async_update_timestamp_in_qbd_direct,
    run_import_export,
    async_update_workspace_name,
    async_create_admin_subcriptions
)

from tests.test_fyle.fixtures import fixtures as fyle_fixtures

from django_q.models import OrmQ
from django.conf import settings
from django.urls import reverse


def test_async_update_fyle_credentials(
    db,
    mocker,
    create_temp_workspace,
    add_fyle_credentials
):
    workspace_id = 1
    org_id = "riseabovehate1"

    async_update_fyle_credentials(
        fyle_org_id=org_id,
        refresh_token="refresh_token"
    )

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    assert fyle_credentials.refresh_token == "refresh_token"


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_run_import_export_bill_ccp(
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        add_field_mappings, add_advanced_settings, add_expenses,
        mocker
):
    """
    Test run import export
    """
    mocker.patch(
        'fyle.platform.apis.v1.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    workspace_id = 1

    run_import_export(workspace_id)

    tasks = OrmQ.objects.all()

    assert tasks.count() == 3


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_run_import_export_journal_journal(
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        add_field_mappings, add_advanced_settings, add_expenses,
        mocker
):
    """
    Test run import export
    """
    workspace_id = 3

    mocker.patch(
        'fyle.platform.apis.v1.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    Expense.objects.filter(workspace_id=workspace_id).all()

    run_import_export(workspace_id)

    tasks = OrmQ.objects.all()

    assert tasks.count() == 3


@pytest.mark.django_db(databases=['default'])
def test_async_update_workspace_name(mocker, create_temp_workspace):
    mocker.patch(
        'apps.workspaces.tasks.get_fyle_admin',
        return_value={'data': {'org': {'name': 'Test Org'}}}
    )
    workspace = Workspace.objects.get(id=1)
    async_update_workspace_name(workspace, 'Bearer access_token')

    workspace = Workspace.objects.get(id=1)
    assert workspace.name == 'Test Org'


def test_async_create_admin_subcriptions(
    db,
    mocker,
    create_temp_workspace,
    add_fyle_credentials
):
    mock_api = mocker.patch(
        'fyle.platform.apis.v1.admin.Subscriptions.post',
        return_value={}
    )
    workspace_id = 1
    async_create_admin_subcriptions(workspace_id=workspace_id)

    payload = {
        'is_enabled': True,
        'webhook_url': '{}/workspaces/{}/fyle/webhook_callback/'.format(settings.API_URL, workspace_id)
    }

    assert mock_api.once_called_with(payload)

    mock_api.side_effect = Exception('Error')
    try:
        async_create_admin_subcriptions(workspace_id=workspace_id)
    except Exception as e:
        assert str(e) == 'Error'


def test_async_create_admin_subcriptions_2(
    db,
    mocker,
    create_temp_workspace,
    add_fyle_credentials
):
    mock_api = mocker.patch(
        'fyle.platform.apis.v1.admin.Subscriptions.post',
        return_value={}
    )
    workspace_id = 1
    reverse('webhook-callback', kwargs={'workspace_id': workspace_id})

    payload = {
        'is_enabled': True,
        'webhook_url': '{}/workspaces/{}/fyle/webhook_callback/'.format(settings.API_URL, workspace_id)
    }

    assert mock_api.once_called_with(payload)

    mock_api.side_effect = Exception('Error')
    reverse('webhook-callback', kwargs={'workspace_id': workspace_id})


def test_handle_webhook_callback_case_1(db, create_temp_workspace):
    """
    Test handle webhook callback
    Case: Valid Payload
    """
    workspace = Workspace.objects.first()

    assert workspace.migrated_to_qbd_direct is False

    payload = {
        'data': {
            'org_id': workspace.org_id
        },
        'action': 'DISABLE_EXPORT'
    }

    async_handle_webhook_callback(payload=payload)

    workspace.refresh_from_db()

    assert workspace.migrated_to_qbd_direct is True


def test_handle_webhook_callback_case_2(db, create_temp_workspace):
    """
    Test handle webhook callback
    Case: Invalid Payload, org_id not present
    """
    workspace = Workspace.objects.first()

    assert workspace.migrated_to_qbd_direct is False

    payload = {
        'data': {
            'org_id': None
        },
        'action': 'DISABLE_EXPORT'
    }

    try:
        async_handle_webhook_callback(payload=payload)
    except ValidationError as e:
        assert str(e.detail[0]) == 'Org Id not found'


def test_handle_webhook_callback_case_3(db, create_temp_workspace):
    """
    Test handle webhook callback
    Case: Invalid Payload, org_id does not match in workspace
    """
    workspace = Workspace.objects.first()

    assert workspace.migrated_to_qbd_direct is False

    payload = {
        'data': {
            'org_id': 'org123'
        },
        'action': 'DISABLE_EXPORT'
    }

    async_handle_webhook_callback(payload=payload)
    assert workspace.migrated_to_qbd_direct is False


def test_handle_webhook_callback_case_4(db, create_temp_workspace):
    """
    Test handle webhook callback
    Case: Invalid Payload, action not present
    """
    workspace = Workspace.objects.first()

    assert workspace.migrated_to_qbd_direct is False

    payload = {
        'data': {
            'org_id': workspace.org_id
        }
    }

    try:
        async_handle_webhook_callback(payload=payload)
    except ValidationError as e:
        assert str(e.detail[0]) == 'Action not found in the webhook callback payload'

    assert workspace.migrated_to_qbd_direct is False


def test_async_update_timestamp_in_qbd_direct_case_1(
    db,
    mocker,
    create_temp_workspace,
    add_fyle_credentials
):
    """
    Test update_timestamp_in_qbd_direct
    Case: Valid Payload and token
    """
    workspace = Workspace.objects.first()
    post_request = mocker.patch('apps.workspaces.tasks.post_request')

    async_update_timestamp_in_qbd_direct(workspace.id)

    post_request.assert_called_once()


def test_async_update_timestamp_in_qbd_direct_case_2(db, create_temp_workspace):
    """
    Test update_timestamp_in_qbd_direct
    Case: Token not present
    """
    workspace = Workspace.objects.first()

    try:
        async_update_timestamp_in_qbd_direct(workspace.id)
    except Exception as e:
        assert str(e.detail[0]) == 'Auth Token not present for workspace id {}'.format(workspace.id)
