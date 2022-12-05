import pytest

from apps.tasks.models import AccountingExport


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_accounting_export_bills():
    """
    Pytest fixture to add accounting export to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        AccountingExport.objects.update_or_create(
            workspace_id=workspace_id,
            type='EXPORT_BILLS',
            defaults={
                'status': 'ENQUEUED'
            }
        )

        AccountingExport.objects.update_or_create(
            workspace_id=workspace_id,
            type='EXPORT_CREDIT_CARD_PURCHASES',
            defaults={
                'status': 'ENQUEUED'
            }
        )

        AccountingExport.objects.update_or_create(
            workspace_id=workspace_id,
            type='EXPORT_JOURNALS',
            defaults={
                'status': 'ENQUEUED'
            }
        )
