from datetime import datetime, timezone
import pytest

from apps.workspaces.models import Workspace, FyleCredential, ExportSettings
from apps.tasks.models import AccountingExport



@pytest.fixture
@pytest.mark.django_db(databases=['default'])
def create_temp_workspace():
    """
    Pytest fixture to create a temorary workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        Workspace.objects.create(
            id=workspace_id,
            name='Fyle For Testing {}'.format(workspace_id),
            org_id='riseabovehate{}'.format(workspace_id),
            reimbursable_last_synced_at=None,
            ccc_last_synced_at=None,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc)
        )

@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_fyle_credentials():
    """
    Pytest fixture to add fyle credentials to a workspace
    """
    workspace_ids = [
        1, 2, 3
    ]
    for workspace_id in workspace_ids:
        FyleCredential.objects.create(
            refresh_token='dummy_refresh_token',
            workspace_id=workspace_id,
            cluster_domain='https://dummy_cluster_domain.com',
        )
