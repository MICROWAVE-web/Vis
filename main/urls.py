from django.contrib import admin
from django.urls import path, include
from .views import Vis, validate_url


urlpatterns = [
    path('admin/', admin.site.urls, name='admin_panel'),
    path('vis/', Vis.as_view(), name='ghome'),
    path('ajax_validate_url/', validate_url)
]
