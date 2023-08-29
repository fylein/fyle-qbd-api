from .helpers import sync_card

def sync_attributes(attribute_type: str, workspace_id: int):
    if attribute_type == 'CORPORATE_CARD':
        sync_card(workspace_id)