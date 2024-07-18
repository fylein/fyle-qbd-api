from django.urls import reverse
import pytest

from apps.mappings.models import QBDMapping

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


def test_sync_fyle_dimension_projects(api_client, test_connection, mocker):
    mocker.patch(
            'fyle.platform.apis.v1beta.admin.projects.list_all',
            return_value=fixture['project_list']
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
    assert len(qbd_mapping) == fixture['get_qbd_ccc_mapping_project']['count']
    assert qbd_mapping[0].source_value == fixture['get_qbd_ccc_mapping_project']['results'][0]['source_value']


def test_sync_fyle_dimension_cost_center(api_client, test_connection, mocker):
    mocker.patch(
            'fyle.platform.apis.v1beta.admin.cost_center.list_all',
            return_value=fixture['cost_center_list']
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
    assert len(qbd_mapping) == fixture['get_qbd_ccc_mapping_cost_center']['count']
    assert qbd_mapping[0].source_value == fixture['get_qbd_ccc_mapping_cost_center']['results'][0]['source_value']