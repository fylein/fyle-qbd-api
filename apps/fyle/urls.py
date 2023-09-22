from django.urls import path

from apps.fyle.views import SyncFyleDimensionView


urlpatterns = [
    path('sync_dimensions/', SyncFyleDimensionView.as_view(), name='sync-fyle-dimensions'),
]
