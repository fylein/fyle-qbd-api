from django.contrib import admin

# Register your models here.
from apps.integration_helper.models import Conversation

admin.site.register(Conversation)
