from django.urls import path
from .views import CoversationsView


urlpatterns = [
    path(route='', view=CoversationsView.as_view(), name='conversations')
]
