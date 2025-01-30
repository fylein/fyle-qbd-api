from apps.workspaces.models import Workspace
from apps.workspaces.tasks import post_to_integration_settings

workspaces = Workspace.objects.filter(onboarding_state='COMPLETE')
for workspace in workspaces:
    print(workspace.id, workspace.name, sep=' | ')
    post_to_integration_settings(workspace.id, True)
