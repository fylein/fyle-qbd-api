from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your models here.
class Query(models.Model):
    id = models.AutoField(primary_key=True)
    query = models.TextField()
    workspace_id = models.IntegerField(help_text="Workspace id of the organization")
    _llm_response = models.JSONField(default={})
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text='Reference to users table')
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Updated at datetime"
    )

    class Meta:
        db_table = 'queries'
