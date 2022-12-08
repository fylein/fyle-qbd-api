"""quickbooks_desktop_api URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from .views import (
    WorkspaceView,
    ExportSettingView,
    AdvancedSettingView,
    FieldMappingView,
    TriggerExportView,
    ReadyView
)


urlpatterns = [
    path('', WorkspaceView.as_view(), name='workspaces'),
    path('ready/', ReadyView.as_view(), name='ready'),
    path('<int:workspace_id>/export_settings/', ExportSettingView.as_view(), name='export-settings'),
    path('<int:workspace_id>/advanced_settings/', AdvancedSettingView.as_view(), name='advanced-settings'),
    path('<int:workspace_id>/field_mappings/', FieldMappingView.as_view(), name='field-mappings'),
    path('<int:workspace_id>/trigger_export/', TriggerExportView.as_view(), name='trigger-export'),
    path('<int:workspace_id>/accounting_exports/', include('apps.tasks.urls'))
]
