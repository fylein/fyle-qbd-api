from apps.mappings.connector import PlatformConnector
from apps.workspaces.models import FieldMapping


def sync_fyle_dimensions(self, workspace_id: int):
    """
    Sync Attributes will be called for syncing the attribute's data from the fyle to qbd db
    """

    qbd_connection = PlatformConnector(workspace_id=workspace_id)
    qbd_connection.sync_corporate_card()

    field_mapping = FieldMapping.objects.filter(workspace_id=self.workspace).first()
	  
    if field_mapping.items_type == 'PROJECT':
        qbd_connection.sync_projects(field_mapping.items_type)
	
    elif field_mapping.items_type == 'COST_CENTER':
        qbd_connection.sync_cost_center(field_mapping.items_type)
		
    elif field_mapping.items_type not in ['PROJECT', 'COST_CENTER']:
        qbd_connection.sync_custom_field_options = True
		
    qbd_connection.sync_custom_field(field_mapping.items_type, field_mapping)