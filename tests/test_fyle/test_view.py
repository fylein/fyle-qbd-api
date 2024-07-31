import json
from django.urls import reverse
import pytest

from apps.mappings.connector import PlatformConnector
from apps.mappings.models import QBDMapping

from apps.workspaces.models import FieldMapping, FyleCredential, User, Workspace
from tests.test_mapping.fixtures import fixture

@pytest.mark.django_db(databases=['default'])
def test_sync_fyle_dimension_view(api_client, test_connection, mocker):
    mocker.patch(
            'fyle.platform.apis.v1beta.admin.corporate_cards.list_all',
            return_value=fixture['credit_card_sdk']
        )
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace_id = response.data['id']

    url = reverse(
        'sync-fyle-dimensions', kwargs={
            'workspace_id': workspace_id
        }
    )

    response = api_client.post(url)

    qbd_mapping = QBDMapping.objects.filter(workspace_id=workspace_id)

    assert response.status_code == 200
    assert len(qbd_mapping) == fixture['get_qbd_ccc_mapping']['count']
    assert qbd_mapping[0].source_value == fixture['get_qbd_ccc_mapping']['results'][0]['source_value']


@pytest.mark.django_db(databases=['default'])
def test_sync_fyle_dimensions_project(api_client, test_connection, mocker):
    workspace_id = 1
    # Create a workspace instance
    Workspace.objects.create(id=workspace_id)
    # Create a FyleCredential instance
    FyleCredential.objects.create(
    refresh_token='dummy_refresh_token',
    workspace_id=workspace_id,
    cluster_domain='https://dummy_cluster_domain.com',
    )
    mocker.patch('apps.mappings.connector.PlatformConnector.sync_corporate_card')
    mocker.patch('apps.mappings.connector.PlatformConnector.sync_projects')
    mocker.patch('apps.mappings.connector.PlatformConnector.sync_custom_field')
    
    # Create a FieldMapping object for PROJECT
    FieldMapping.objects.create(
        workspace_id=workspace_id,
        item_type='PROJECT'
    )

    url = reverse('sync-fyle-dimensions', kwargs={'workspace_id': workspace_id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    assert response.status_code == 200
    PlatformConnector.sync_corporate_card.assert_called_once()
    PlatformConnector.sync_projects.assert_called_once_with('PROJECT')
    PlatformConnector.sync_custom_field.assert_called_once()


@pytest.mark.django_db(databases=['default'])
def test_sync_fyle_dimensions_cost_center(api_client, test_connection, mocker):
    workspace_id = 1
    # Create a workspace instance
    Workspace.objects.create(id=workspace_id)
    # Create a FyleCredential instance
    FyleCredential.objects.create(
    refresh_token='dummy_refresh_token_1',
    workspace_id=workspace_id,
    cluster_domain='https://anish.com',
    )
    mocker.patch('apps.mappings.connector.PlatformConnector.sync_corporate_card')
    mocker.patch('apps.mappings.connector.PlatformConnector.sync_cost_center')
    mocker.patch('apps.mappings.connector.PlatformConnector.sync_custom_field')
    
    # Create a FieldMapping object for COST_CENTER
    FieldMapping.objects.create(
        workspace_id=workspace_id,
        item_type='COST_CENTER'
    )

    url = reverse('sync-fyle-dimensions', kwargs={'workspace_id': workspace_id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    assert response.status_code == 200
    PlatformConnector.sync_corporate_card.assert_called_once()
    PlatformConnector.sync_cost_center.assert_called_once_with('COST_CENTER')
    PlatformConnector.sync_custom_field.assert_called_once()


@pytest.mark.django_db(databases=['default'])
def test_custom_fields(mocker, api_client, test_connection):
    access_token = test_connection.access_token

    # Create a Workspace object
    Workspace.objects.create(id=1)

    # Create a FyleCredential object
    FyleCredential.objects.create(workspace_id=1)

    url = reverse('custom-field', kwargs={'workspace_id': 1})

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.expense_fields.list_all',
        return_value=fixture['get_all_custom_fields']
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response_data = json.loads(response.content)

    # Check if response data is a list of field names
    assert isinstance(response_data, list)
    assert all(isinstance(field, str) for field in response_data)