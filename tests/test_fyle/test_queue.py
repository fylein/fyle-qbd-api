import pytest
from django_q.models import OrmQ

from apps.fyle.queue import queue_import_reimbursable_expenses, queue_import_credit_card_expenses
from apps.tasks.models import AccountingExport


@pytest.mark.django_db(databases=['default'])
def test_queue_import_reimbursable_expenses(create_temp_workspace):
    """
    Test queue import reimbursable expenses
    """
    workspace_id = 1
    queue_import_reimbursable_expenses(workspace_id)

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    
    tasks = OrmQ.objects.all()
    
    assert accounting_export.status == 'IN_PROGRESS'
    assert tasks.count() == 1
    


@pytest.mark.django_db(databases=['default'])
def test_queue_import_credit_card_expenses(create_temp_workspace):
    """
    Test queue import credit card expenses
    """
    workspace_id = 1
    queue_import_credit_card_expenses(workspace_id)

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    
    tasks = OrmQ.objects.all()

    assert accounting_export.status == 'IN_PROGRESS'
    assert tasks.count() == 1
