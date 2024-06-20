import pytest
from apps.fyle.models import Expense
from apps.workspaces.models import Workspace
from apps.workspaces.tasks import (
    run_import_export,
    async_update_workspace_name,
    async_create_admin_subcriptions
)

from tests.test_fyle.fixtures import fixtures as fyle_fixtures

from django_q.models import OrmQ
from django.conf import settings
from django.urls import reverse


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
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    workspace_id = 1

    run_import_export(workspace_id)

    tasks = OrmQ.objects.all()

    assert tasks.count() == 2


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
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    Expense.objects.filter(workspace_id=workspace_id).all()

    run_import_export(workspace_id)

    tasks = OrmQ.objects.all()

    assert tasks.count() == 2


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
        'fyle.platform.apis.v1beta.admin.Subscriptions.post',
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
        'fyle.platform.apis.v1beta.admin.Subscriptions.post',
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
