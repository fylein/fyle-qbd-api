import pytest
from apps.mappings import connector
from apps.mappings.connector import PlatformConnector
from apps.mappings.models import QBDMapping
from apps.workspaces.models import FieldMapping, FyleCredential, Workspace
from tests.conftest import add_field_mappings
from .fixtures import fixture


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
    assert len(qbd_mappings) == len(fixture['get_qbd_ccc_mapping']['results'])
    for i, _ in enumerate(qbd_mappings):
        assert qbd_mappings[i].source_value == fixture['get_qbd_ccc_mapping']['results'][i]['source_value']

@pytest.mark.django_db(databases=['default'], transaction=True)
def test_sync_projects(create_temp_workspace, add_fyle_credentials, mocker):
    workspace_id = 1
    source_type = 'PROJECT'
    mock_response = [
        {'data': [
            {'id': 1, 'name': 'Project 1', 'sub_project': 'Sub Project 1'},
            {'id': 2, 'name': 'Project 2', 'sub_project': 'Sub Project 1'}
        ]}
    ]
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.projects.list_all',
        return_value=mock_response
    )
    qbd_connection = PlatformConnector(workspace_id=workspace_id)
    qbd_connection.sync_projects(source_type)
    qbd_mappings = QBDMapping.objects.filter(workspace_id=workspace_id, attribute_type=source_type)
    assert len(qbd_mappings) == 2
    mapping = qbd_mappings.first()
    assert mapping.source_value == 'Project 1 / Sub Project 1'

@pytest.mark.django_db(databases=['default'], transaction=True)
def test_sync_cost_center(create_temp_workspace, add_fyle_credentials, mocker):
    workspace_id = 1
    source_type = 'COST_CENTER'
    mock_response = [
        {'data': [{'name': 'Cost Center 1', 'id': 1}]}
    ]
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.cost_centers.list_all',
        return_value=mock_response
    )
    qbd_connection = PlatformConnector(workspace_id=workspace_id)
    qbd_connection.sync_cost_center(source_type)
    qbd_mappings = QBDMapping.objects.filter(workspace_id=workspace_id, attribute_type=source_type)
    assert len(qbd_mappings) == len(mock_response[0]['data'])
    for i, mapping in enumerate(qbd_mappings):
        cost_center = mock_response[0]['data'][i]
        assert mapping.source_value == 'Cost Center 1'


@pytest.mark.django_db(databases=['default'], transaction=True)
def test_sync_custom_field(mocker, api_client, test_connection):
    access_token = test_connection.access_token

    # Create a Workspace object
    Workspace.objects.create(id=1)

    # Create a FyleCredential object
    FyleCredential.objects.create(workspace_id=1)

    # Create a FieldMapping object
    field_mapping, _ = FieldMapping.objects.get_or_create(workspace_id=1, 
                                                       custom_fields=[{'data': [{'field_name': 'field1', 'options': ['option1', 'option2']}]}])

    # Mock the platform API call
    custom_fields_response = [
        {'data': [{'field_name': 'field1', 'options': ['option1', 'option2']}]},
        {'data': [{'field_name': 'field2', 'options': ['option3', 'option4']}]}
    ]
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.expense_fields.list_all',
        return_value=custom_fields_response
    )

    # Create a PlatformConnector instance
    platform_connector = PlatformConnector(workspace_id=1)

    # Call the sync_custom_field function
    platform_connector.sync_custom_field(field_mapping, 'field1', sync_expense_custom_field_names=True)

    # Check if custom fields are updated in FieldMapping
    field_mapping.refresh_from_db()
    assert field_mapping.custom_fields == ['field1', 'field2']

    # Check if QBDMapping objects are created
    qbd_mappings = QBDMapping.objects.filter(workspace_id=1, attribute_type='field1')
    assert qbd_mappings.count() == 2
    assert qbd_mappings.filter(source_value='option1').exists()
    assert qbd_mappings.filter(source_value='option2').exists()