from django.urls import reverse
from apps.tasks.models import AccountingExport

from tests.test_fyle.fixtures import fixtures as fyle_fixtures


def test_list_accounting_exports(
    api_client, test_connection
):
    '''
    Test post of workspace
    '''
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
        'reimbursable_expense_date': 'last_spent_at',
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

    # test with `type` filter
    response = api_client.get(url, {'type': 'FETCHING_REIMBURSABLE_EXPENSES,FETCHING_CREDIT_CARD_EXPENSES'})

    assert response.status_code == 200
    assert response.data['count'] == 1

    # test with `status` filter
    response = api_client.get(url, {'status': 'COMPLETE,IN_PROGRESS'})

    assert response.status_code == 200
    assert response.data['count'] == 2

    # test with 'id' filter
    response = api_client.get(url, {'id': [export_1.id]})

    assert response.status_code == 200
    assert response.data['count'] == 1

    # test with start_date and end_date filter
    response = api_client.get(url, {'start_date': '2021-01-01', 'end_date': '2050-12-31'})

    assert response.status_code == 200
    assert response.data['count'] == 1


def test_accounting_export_download(api_client, test_connection, mocker):
    '''
    Test post of workspace
    '''
    mocker.patch(
        'fyle.platform.apis.v1.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)

    workspace_id = response.data['id']

    export, _ = AccountingExport.objects.update_or_create(
        workspace_id=workspace_id,
        type='EXPORT_CREDIT_CARD_PURCHASES',
        defaults={
            'status': 'COMPLETE',
            'file_id': 'fimNloQVF0D8'
        }
    )
    url = reverse(
        'accounting-export-download',
        kwargs={
            'workspace_id': workspace_id,
            'accounting_export_id': export.id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)

    assert response.status_code == 200
    assert response.data['file_id'] == 'fimNloQVF0D8'
    assert response.data['accounting_export_id'] == export.id    
