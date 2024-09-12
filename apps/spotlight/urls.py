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
from django.urls import path

from apps.spotlight.views import HelpQueryView, \
    QueryView, RecentQueryView, ActionQueryView, SuggestionForPage



urlpatterns = [
    path('recent_queries/', RecentQueryView.as_view(), name='recent-queries'),
    path('query/', QueryView.as_view(), name='query'),
    path('help/', HelpQueryView.as_view(), name='help'),
    path('action/', ActionQueryView.as_view(), name='action'),
    path('suggest_actions/', SuggestionForPage.as_view(), name='suggestion')
]
