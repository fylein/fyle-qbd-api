from django.urls import reverse
import pytest

from apps.mappings.helpers import sync_card
from apps.mappings.models import QBDMapping

from .fixture import fixture

@pytest.mark.django_db(databases=['default'])
def test_qbd_mapping_view(api_client, test_connection, mocker):
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
        'QBD-Mapping', kwargs={
            'workspace_id': workspace_id
        }
    )

    # get all rows of qbo mapping table
    response = api_client.get(url, {'attribute_type': 'CORPORATE_CARD', 'limit':10, 'offset':0})

    assert response.status_code == 200
    assert len(response.data['results']) == len(fixture['get_qbd_CCC_mapping']['results'])
    assert response.data['count'] == fixture['get_qbd_CCC_mapping']['count']

    # post qbd mapping
    url = reverse(
        'QBD-Mapping', kwargs={
            'workspace_id': workspace_id
        }
    )
    payload = {
        "id": 3,
        "destination_value": "Mastercard",
        "attribute_type": "CORPORATE_CARD",
        "source_id": "bacc1DHywC3YAd",
        "source_value": "American Express - 055470",
        "workspace": 1
    }
    response = api_client.post(url,payload)

    post_value = QBDMapping.objects.filter(workspace_id=workspace_id, attribute_type = payload['attribute_type'], source_id = payload['source_id'])
    assert response.status_code == 201
    assert post_value[0].destination_value == payload['destination_value']

    # get all mapped rows (destination_value__isnull is false)

    response = api_client.get(url, {'attribute_type': 'CORPORATE_CARD', 'limit':10, 'offset':0, 'destination_value__isnull': 'false'})

    assert response.status_code == 200
    assert len(response.data['results']) == len(fixture['get_qbd_CCC_mapping']['results'])-1
    assert response.data['count'] == fixture['get_qbd_CCC_mapping']['count']-1
    assert response.data['results'][0]['source_value'] == fixture['get_qbd_CCC_mapping']['results'][0]['source_value']

    # get all unmapped rows (destination_value__isnull is true)

    response = api_client.get(url, {'attribute_type': 'CORPORATE_CARD', 'limit':10, 'offset':0, 'destination_value__isnull': 'true'})

    assert response.status_code == 200
    assert len(response.data['results']) == len(fixture['get_qbd_CCC_mapping']['results'])-1
    assert response.data['count'] == fixture['get_qbd_CCC_mapping']['count']-1
    assert response.data['results'][0]['source_value'] == fixture['get_qbd_CCC_mapping']['results'][1]['source_value']

@pytest.mark.django_db(databases=['default'])
def test_qbd_mapping_stats_view(api_client, test_connection):
    qbd_mapping_count = QBDMapping.objects.filter(workspace_id=2, attribute_type = 'CORPORATE_CARD').count()
    if qbd_mapping_count == 0:
        QBDMapping.update_or_create_mapping_objects(fixture['create_qbd_mapping'], 2)
    url = reverse(
        'workspaces'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)

    workspace_id = response.data['id']

    url = reverse(
        'QBD-Mapping-stats', kwargs={
            'workspace_id': workspace_id
        }
    )

    response = api_client.get(url, {'source_type': 'CORPORATE_CARD'})

    assert response.status_code == 200
    assert response.data['all_attributes_count'] == fixture['get_qbd_CCC_mapping_state']['all_attributes_count']
    assert response.data['unmapped_attributes_count'] == fixture['get_qbd_CCC_mapping_state']['unmapped_attributes_count']