from datetime import datetime, timedelta, time
from .models import AdvancedSetting
from django_q.models import Schedule


def __get_time_inputstamp_from_time_input_and_weekday(day_of_the_week: str, time_input: time):
    """
    Get next run value based on day of week and time_input
    Day of the week values will be day names
    """
    days_of_the_week = {
        'MONDAY': 0,
        'TUESDAY': 1,
        'WEDNESDAY': 2,
        'THURSDAY': 3,
        'FRIDAY': 4,
        'SATURDAY': 5,
        'SUNDAY': 6
    }

    day_of_the_week = days_of_the_week[day_of_the_week]
    time_input = str(time_input).split(':')
    hour = int(time_input[0])
    minute = int(time_input[1])

    next_run = datetime.now()

    if next_run.weekday() == day_of_the_week:
        if next_run.hour > hour:
            next_run = next_run + timedelta(days=7)
        elif next_run.hour == hour:
            if next_run.minute > minute:
                next_run = next_run + timedelta(days=7)
    elif next_run.weekday() > day_of_the_week:
        next_run = next_run + timedelta(days=7)

    next_run = next_run.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    return next_run


def __get_time_inputstamp_from_time_input_and_day_of_month(day_of_month: int, time_input: time):
    """
    Get next run value based on day of month and time_input
    """
    time_input = str(time_input).split(':')
    hour = int(time_input[0])
    minute = int(time_input[1])

    next_run = datetime.now()

    if next_run.day > day_of_month:
        next_run = next_run + timedelta(days=30)
    elif next_run.day == day_of_month:
        if next_run.hour > hour:
            next_run = next_run + timedelta(days=30)
        elif next_run.hour == hour:
            if next_run.minute > minute:
                next_run = next_run + timedelta(days=30)

    next_run = next_run.replace(
        day=day_of_month,
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    return next_run



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
        frequency = advanced_settings.frequency

        if frequency == 'DAILY':
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.workspaces.tasks.run_import_export',
                args=f'{workspace_id}',
                defaults={
                    'schedule_type': Schedule.DAILY,
                    'time_input': advanced_settings.time_input_of_day,
                    'next_run': datetime.now()
                }
            )
        elif frequency == 'WEEKLY':
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.workspaces.tasks.run_import_export',
                args=f'{workspace_id}',
                defaults={
                    'schedule_type': Schedule.WEEKLY,
                    'next_run': __get_time_inputstamp_from_time_input_and_weekday(
                        advanced_settings.day_of_week,
                        advanced_settings.time_input_of_day
                    )
                }
            )
        elif frequency == 'MONTHLY':
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.workspaces.tasks.run_import_export',
                args=f'{workspace_id}',
                defaults={
                    'schedule_type': Schedule.MONTHLY,
                    'next_run': __get_time_inputstamp_from_time_input_and_day_of_month(
                        advanced_settings.day_of_month,
                        advanced_settings.time_input_of_day
                    )
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
