from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet

router = DefaultRouter()
router.register(r'conversation', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
]
