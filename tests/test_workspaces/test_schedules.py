import pytest

from django_q.models import Schedule
from apps.workspaces.models import AdvancedSetting

from apps.workspaces.schedule import schedule_run_import_export


@pytest.mark.django_db(databases=['default'])
def test_schedule_run_import_export_enabled(
        create_temp_workspace, add_accounting_export_expenses, 
        add_fyle_credentials, add_export_settings, 
        add_field_mappings, add_advanced_settings,
        mocker
    ):
    """
    Test schedule run import export
    """
    workspace_id = 1
    schedule_run_import_export(workspace_id)

    schedules = Schedule.objects.all()

    assert schedules.count() == 1

    AdvancedSetting.objects.filter(workspace_id=workspace_id).update(schedule_is_enabled=False)

    schedule_run_import_export(workspace_id)

    schedules = Schedule.objects.all()

    assert schedules.count() == 0