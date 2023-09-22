from apps.mappings.connector import PlatformConnector


def sync_fyle_dimensions(workspace_id: int):
    """
    Sync Attributes will be called for syncing the attribute's data from the fyle to qbd db
    """

    qbd_connection = PlatformConnector(workspace_id=workspace_id)
    qbd_connection.sync_corporate_card()
