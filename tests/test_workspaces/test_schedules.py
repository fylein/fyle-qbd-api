from datetime import time
import logging
import pytest

from django_q.models import Schedule
from apps.workspaces.models import AdvancedSetting

from apps.workspaces.schedule import (
    schedule_run_import_export,
    __get_daily_crontab,
    __get_weekly_crontab,
    __get_monthly_crontab
)

logger = logging.getLogger('app')

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

    # schedules = Schedule.objects.all()

    # assert schedules.count() == 1

    AdvancedSetting.objects.filter(workspace_id=workspace_id).update(schedule_is_enabled=False)

    # Create 3 cases for daily, weekly and monthly
    # Daily
    AdvancedSetting.objects.filter(workspace_id=workspace_id).update(
        schedule_is_enabled=True,
        frequency='DAILY',
        time_of_day=time(12, 0)
    )

    schedule_run_import_export(workspace_id)

    schedules = Schedule.objects.filter(args=str(workspace_id)).all()

    assert schedules.count() == 1
    assert schedules[0].cron == '0 12 * * *'

    # Weekly
    AdvancedSetting.objects.filter(workspace_id=workspace_id).update(
        schedule_is_enabled=True,
        frequency='WEEKLY',
        day_of_week='MONDAY',
        time_of_day=time(12, 0)
    )

    schedule_run_import_export(workspace_id)

    schedules = Schedule.objects.filter(args=str(workspace_id)).all()
    
    assert schedules.count() == 1
    assert schedules[0].cron == '0 12 * * 1'

    # Monthly
    AdvancedSetting.objects.filter(workspace_id=workspace_id).update(
        schedule_is_enabled=True,
        frequency='MONTHLY',
        day_of_month=1,
        time_of_day=time(12, 0)
    )

    schedule_run_import_export(workspace_id)

    schedules = Schedule.objects.filter(args=str(workspace_id)).all()

    assert schedules.count() == 1
    assert schedules[0].cron == '0 12 1 * *'

    # Disable schedule
    AdvancedSetting.objects.filter(workspace_id=workspace_id).update(schedule_is_enabled=False)

    schedule_run_import_export(workspace_id)

    schedules = Schedule.objects.filter(args=str(workspace_id)).all()

    assert schedules.count() == 0


@pytest.mark.django_db(databases=['default'])
def test_get_daily_crontab():
    """
    Test get timestamp from time input and weekday
    """
    time_input = time(12, 0)
    crontab = __get_daily_crontab(time_input)

    assert crontab == '0 12 * * *'


@pytest.mark.django_db(databases=['default'])
def test_get_weekly_crontab():
    """
    Test get timestamp from time input and weekday
    """
    time_input = time(12, 0)
    crontab = __get_weekly_crontab('MONDAY', time_input)

    assert crontab == '0 12 * * 1'


@pytest.mark.django_db(databases=['default'])
def test_get_monthly_crontab():
    """
    Test get timestamp from time input and weekday
    """
    time_input = time(12, 0)
    crontab = __get_monthly_crontab(1, time_input)

    assert crontab == '0 12 1 * *'
