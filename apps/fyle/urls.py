from django.urls import path

from apps.fyle.views import CustomFieldView, SyncFyleDimensionView, WebhookCallbackView


urlpatterns = [
    path('sync_dimensions/', SyncFyleDimensionView.as_view(), name='sync-fyle-dimensions'),
    path('webhook_callback/', WebhookCallbackView.as_view(), name='webhook-callback'),
    path('custom_fields/', CustomFieldView.as_view(), name='custom-field'),
]
