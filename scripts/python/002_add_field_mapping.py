# Create field mapping for existing workspaces

from apps.workspaces.models import Workspace, FieldMapping

workspaces = Workspace.objects.exclude(fieldmapping__isnull=False)

for workspace in workspaces:
    try:
        FieldMapping.objects.create(workspace_id = workspace.id)
        print('Field mapping created for workspace - {} with ID - {}'.format(workspace.name, workspace.id))
    except Exception as e:
        print('Error while creating field mapping for workspace - {} with ID - {}'.format(workspace.name, workspace.id))
        print(e.__dict__)
