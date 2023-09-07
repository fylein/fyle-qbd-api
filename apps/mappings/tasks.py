from .connector import PlatformConnector


def sync_attributes(attribute_type: str, workspace_id: int):
    """
    Sync Attributes will be called for syncing the attribute's data from the fyle to qbd db
    """

    qbd_connection = PlatformConnector(workspace_id=workspace_id)

    if attribute_type == 'CORPORATE_CARD':
        qbd_connection.sync_corporate_card()
