import pytest
from apps.mappings.connector import PlatformConnector
from apps.mappings.models import QBDMapping
from .fixture import fixture


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_sync_corporate_card(create_temp_workspace,
    add_accounting_export_expenses, mocker,
    add_fyle_credentials, add_export_settings):

    workspace_id = 1
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.corporate_cards.list_all',
        return_value=fixture['credit_card_sdk']
    )
    qbd_connection = PlatformConnector(workspace_id=workspace_id)
    qbd_connection.sync_corporate_card()
    qbd_mappings = QBDMapping.objects.filter(workspace_id=workspace_id, attribute_type = 'CORPORATE_CARD')
    assert len(qbd_mappings) == len(fixture['get_qbd_CCC_mapping']['results'])
    for i, item in enumerate(qbd_mappings):
        assert qbd_mappings[i].source_value == fixture['get_qbd_CCC_mapping']['results'][i]['source_value']

