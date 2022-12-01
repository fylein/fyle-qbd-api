import pytest

from apps.fyle.tasks import import_reimbursable_expenses, import_credit_card_expenses
from apps.workspaces.models import Workspace, ExportSettings, FyleCredential
from apps.tasks.models import AccountingExport


@pytest.mark.django_db(databases=['default'])
def test_import_reimbursable_expenses(create_temp_workspace):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    pass


@pytest.mark.django_db(databases=['default'])
def test_import_credit_card_expenses():
    """
    Test import credit card expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    pass
