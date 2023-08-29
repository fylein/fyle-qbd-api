import pytest
from apps.mappings.helpers import sync_card
from apps.mappings.models import QBDMapping
from .fixture import fixture

@pytest.mark.django_db(databases=['default'], transaction=True)
def test_sync_card(create_temp_workspace, 
        add_accounting_export_expenses, 
        add_fyle_credentials, 
        add_export_settings, 
        mocker):
        workspace_id = 1
        mocker.patch(
            'fyle.platform.apis.v1beta.admin.corporate_cards.list_all',
            return_value=fixture['credit_card_sdk']
        )
        sync_card(workspace_id)
        qbd_mappings = QBDMapping.objects.filter(workspace_id=1, attribute_type = 'CORPORATE_CARD')
        assert len(qbd_mappings) == len(fixture['get_qbd_CCC_mapping']['results'])
        for i in range(0,len(qbd_mappings)):
            assert qbd_mappings[i].source_value == fixture['get_qbd_CCC_mapping']['results'][i]['source_value']
