from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Workspace(models.Model):
    """
    Workspace model
    """
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    name = models.CharField(max_length=255, help_text='Name of the workspace')
    user = models.ManyToManyField(User, help_text='Reference to users table')
    org_id = models.CharField(max_length=255, help_text='org id', unique=True)
    cluster_domain = models.CharField(max_length=255, help_text='fyle cluster domain', null=True)
    last_synced_at = models.DateTimeField(help_text='Datetime when expenses were pulled last', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'workspaces'
