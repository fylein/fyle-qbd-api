from django.db import models


class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    conversation_id = models.CharField(max_length=255, help_text="Unique id of the conversation")
    role = models.CharField(max_length=255, help_text="Role of the messenger")
    content = models.TextField(help_text="Content of the message")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )

    class Meta:
        db_table = 'conversations'
