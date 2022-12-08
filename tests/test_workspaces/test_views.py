import json

from django.urls import reverse
import pytest

from apps.workspaces.models import AdvancedSetting, ExportSettings, Workspace


def test_post_of_workspace(api_client, test_connection):
    '''
    Test post of workspace
    '''
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace = Workspace.objects.filter(org_id='orNoatdUnm1w').first()

    assert response.status_code == 201
    assert workspace.name == response.data['name']
    assert workspace.org_id == response.data['org_id']
    assert workspace.currency == response.data['currency']

    response = json.loads(response.content)

    response = api_client.post(url)
    assert response.status_code == 201


def test_get_of_workspace(api_client, test_connection):
    '''
    Test get of workspace
    '''
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)

    assert response.status_code == 400
    assert response.data['message'] == 'org_id is missing'

    response = api_client.get('{}?org_id=orNoatdUnm1w'.format(url))

    assert response.status_code == 400
    assert response.data['message'] == 'Workspace not found'

    response = api_client.post(url)
    response = api_client.get('{}?org_id=orNoatdUnm1w'.format(url))

    assert response.status_code == 200
    assert response.data['name'] == 'Fyle For MS Dynamics Demo'
    assert response.data['org_id'] == 'orNoatdUnm1w'
    assert response.data['currency'] == 'USD'


def test_export_settings(api_client, test_connection):
    '''
    Test export settings
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
    response = api_client.post(url)

    assert response.status_code == 400

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

    response = api_client.post(url, payload)

    export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()

    assert response.status_code == 201
    assert export_settings.reimbursable_expenses_export_type == 'BILL'
    assert export_settings.bank_account_name == 'Accounts Payable'
    assert export_settings.reimbursable_expense_state == 'PAYMENT_PROCESSING'
    assert export_settings.reimbursable_expense_date == 'last_spent_at'
    assert export_settings.reimbursable_expense_grouped_by == 'REPORT'
    assert export_settings.credit_card_expense_export_type == 'CREDIT_CARD_PURCHASE'
    assert export_settings.credit_card_expense_state == 'PAYMENT_PROCESSING'
    assert export_settings.credit_card_entity_name_preference == 'VENDOR'
    assert export_settings.credit_card_account_name == 'Visa'
    assert export_settings.credit_card_expense_grouped_by == 'EXPENSE'
    assert export_settings.credit_card_expense_date == 'spent_at'

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['reimbursable_expenses_export_type'] == 'BILL'
    assert response.data['bank_account_name'] == 'Accounts Payable'
    assert response.data['reimbursable_expense_state'] == 'PAYMENT_PROCESSING'
    assert response.data['reimbursable_expense_date'] == 'last_spent_at'
    assert response.data['reimbursable_expense_grouped_by'] == 'REPORT'
    assert response.data['credit_card_expense_export_type'] == 'CREDIT_CARD_PURCHASE'
    assert response.data['credit_card_expense_state'] == 'PAYMENT_PROCESSING'
    assert response.data['credit_card_entity_name_preference'] == 'VENDOR'
    assert response.data['credit_card_account_name'] == 'Visa'
    assert response.data['credit_card_expense_grouped_by'] == 'EXPENSE'
    assert response.data['credit_card_expense_date'] == 'spent_at'


def test_field_mappings(api_client, test_connection):
    '''
    Test field mappings
    '''
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace_id = response.data['id']

    url = reverse(
        'field-mappings', kwargs={
            'workspace_id': workspace_id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    payload = {
        'class_type': 'COST_CENTER',
        'project_type': 'PROJECT'
    }

    response = api_client.post(url, payload)
    
    assert response.status_code == 201
    assert response.data['class_type'] == 'COST_CENTER'
    assert response.data['project_type'] == 'PROJECT'

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['class_type'] == 'COST_CENTER'
    assert response.data['project_type'] == 'PROJECT'


def test_advanced_settings(api_client, test_connection):
    '''
    Test advanced settings
    '''
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace_id = response.data['id']

    url = reverse(
        'advanced-settings', kwargs={
            'workspace_id': workspace_id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    payload = {
        'memo_structure': [
            'employee_email',
            'merchant',
            'purpose',
            'report_number',
            'expense_link'
        ],
        'schedule_is_enabled': False,
        'interval_hours': 100,
        'emails': [
            'shwetabh.kumar@fylehq.com'
        ]
    }

    response = api_client.post(url, payload)
    
    assert response.status_code == 201
    assert response.data['memo_structure'] == [
        'employee_email',
        'merchant',
        'purpose',
        'report_number',
        'expense_link'
    ]
    assert response.data['schedule_is_enabled'] == False
    assert response.data['interval_hours'] == 100
    assert response.data['schedule_id'] == None
    assert response.data['emails'] == [
        'shwetabh.kumar@fylehq.com'
    ]

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['memo_structure'] == [
        'employee_email',
        'merchant',
        'purpose',
        'report_number',
        'expense_link'
    ]
    assert response.data['schedule_is_enabled'] == False
    assert response.data['interval_hours'] == 100
    assert response.data['schedule_id'] == None
    assert response.data['emails'] == [
        'shwetabh.kumar@fylehq.com'
    ]

    del payload['memo_structure']

    AdvancedSetting.objects.filter(workspace_id=workspace_id).first().delete()

    response = api_client.post(url, payload)
    
    assert response.status_code == 201
    assert response.data['memo_structure'] == [
        'employee_email',
        'merchant',
        'purpose',
        'report_number'
    ]
    assert response.data['schedule_is_enabled'] == False
    assert response.data['interval_hours'] == 100
    assert response.data['schedule_id'] == None
    assert response.data['emails'] == [
        'shwetabh.kumar@fylehq.com'
    ]


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_trigger_export_view(
    api_client, test_connection, 
    create_temp_workspace, add_export_settings
):
    '''
    Test trigger export view
    '''
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace_id = response.data['id']

    ExportSettings.objects.filter(workspace_id=1).update(workspace_id=workspace_id)

    url = reverse(
        'trigger-export', kwargs={
            'workspace_id': workspace_id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)

    assert response.status_code == 200
    assert response.data['message'] == 'Export triggered successfully'
