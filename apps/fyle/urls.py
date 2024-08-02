from django.urls import path

from apps.fyle.views import SyncFyleDimensionView, WebhookCallbackView


urlpatterns = [
    path('sync_dimensions/', SyncFyleDimensionView.as_view(), name='sync-fyle-dimensions'),
    path('webhook_callback/', WebhookCallbackView.as_view(), name='webhook-callback')
]
