from .models import QBDMapping


def get_qbd_mapping_stat(source_type: str, workspace_id: int):
    """
    get qbd mapping stat will return the count of total mappings available and unmapped mappings
    """
    total_attributes_count = QBDMapping.objects.filter(
        workspace_id=workspace_id,
        attribute_type = source_type
    ).count()

    unmapped_attributes_count = QBDMapping.objects.filter(
        workspace_id=workspace_id,
        attribute_type = source_type,
        destination_value__isnull=True
    ).count()

    return {
        'all_attributes_count': total_attributes_count,
        'unmapped_attributes_count': unmapped_attributes_count
    }
