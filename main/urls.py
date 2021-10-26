from django.contrib import admin
from django.urls import path

from .views import Vis, validate_url, waprfile
urlpatterns = [
    path('admin/', admin.site.urls, name='admin_panel'),
    path('vis/', Vis.as_view(), name='home'),
    path('download/', waprfile, name='download'),
    path('ajax_validate_url/', validate_url)
]
