from datetime import datetime
from .models import AdvancedSetting
from django_q.models import Schedule


def schedule_run_import_export(workspace_id: int):
    """
    Schedule Run Import Export
    """
    advanced_settings = AdvancedSetting.objects.get(
        workspace_id=workspace_id
    )

    if advanced_settings.schedule_is_enabled:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_import_export',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': advanced_settings.interval_hours * 60,
                'next_run': datetime.now()
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
