from datetime import time
from .models import AdvancedSetting
from django_q.models import Schedule


def __get_weekly_crontab(day_of_the_week: str, time_input: time):
    """
    Create Weekly cron schedule string for day of the week and time_input
    Day of the week values will be day names
    """
    day_of_week = {
        'SUNDAY': 0,
        'MONDAY': 1,
        'TUESDAY': 2,
        'WEDNESDAY': 3,
        'THURSDAY': 4,
        'FRIDAY': 5,
        'SATURDAY': 6
    }

    time_input = str(time_input).split(':')
    hour = int(time_input[0])
    minute = int(time_input[1])

    # Return corntab string
    hour = str(hour)
    minute = str(minute)
    day_of_week = str(day_of_week[day_of_the_week])

    return f'{minute} {hour} * * {day_of_week}'


def __get_monthly_crontab(day_of_month: int, time_input: time):
    """
    Create Monthly cron schedule string for day of the month and time_input
    """
    time_input = str(time_input).split(':')
    hour = int(time_input[0])
    minute = int(time_input[1])

    # Return corntab string
    hour = str(hour)
    minute = str(minute)
    day_of_month = str(day_of_month)

    return f'{minute} {hour} {day_of_month} * *'


def __get_daily_crontab(time_input: time):
    """
    Create Daily cron schedule string for time_input
    """
    time_input = str(time_input).split(':')
    hour = int(time_input[0])
    minute = int(time_input[1])

    # Return corntab string
    hour = str(hour)
    minute = str(minute)

    return f'{minute} {hour} * * *'


def schedule_run_import_export(workspace_id: int):
    """
    Schedule Run Import Export
    Frequency: Daily / Weekly / Monthly
    Weekly: Day of the week : day_of_week, time_input of the day: start_time_input
    Monthly: Day of the month: day_of_month, time_input of the day: start_time_input
    Daily: time_input of the day: time_input_of_day
    """
    advanced_settings = AdvancedSetting.objects.get(
        workspace_id=workspace_id
    )

    if advanced_settings.schedule_is_enabled:
        crontab = None

        if advanced_settings.frequency == 'DAILY':
            crontab = __get_daily_crontab(advanced_settings.time_of_day)
        elif advanced_settings.frequency == 'WEEKLY':
            crontab = __get_weekly_crontab(advanced_settings.day_of_week, advanced_settings.time_of_day)
        elif advanced_settings.frequency == 'MONTHLY':
            crontab = __get_monthly_crontab(advanced_settings.day_of_month, advanced_settings.time_of_day)

        if crontab:
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.workspaces.tasks.run_import_export',
                args=str(workspace_id),
                defaults={
                    'name': 'Run Import Export',
                    'schedule_type': Schedule.CRON,
                    'cron': crontab
                }
            )

            advanced_settings.schedule_id = schedule.id

        advanced_settings.save()

    elif not advanced_settings.schedule_is_enabled:
        schedule = Schedule.objects.filter(id=advanced_settings.schedule_id).first()
        advanced_settings.schedule_id = None
        advanced_settings.save()
        if schedule:
            schedule.delete()

    return advanced_settings
