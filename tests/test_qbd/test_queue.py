import pytest
from django_q.models import OrmQ

from apps.qbd.queue import queue_create_bills_iif_file, queue_create_credit_card_purchases_iif_file
from apps.tasks.models import AccountingExport


@pytest.mark.django_db(databases=['default'])
def test_queue_import_reimbursable_expenses(create_temp_workspace):
    """
    Test queue import reimbursable expenses
    """
    workspace_id = 1
    queue_create_bills_iif_file(workspace_id)

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='EXPORT_BILLS')
    
    tasks = OrmQ.objects.all()
    
    assert accounting_export.status == 'ENQUEUED'
    assert tasks.count() == 1


@pytest.mark.django_db(databases=['default'])
def test_queue_import_credit_card_purchases(create_temp_workspace):
    """
    Test queue import credit card purchases
    """
    workspace_id = 1
    queue_create_credit_card_purchases_iif_file(workspace_id)

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='EXPORT_CREDIT_CARD_PURCHASES')
    
    tasks = OrmQ.objects.all()
    
    assert accounting_export.status == 'ENQUEUED'
    assert tasks.count() == 1
