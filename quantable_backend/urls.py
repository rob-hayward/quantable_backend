# quantable_backend/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentech_app.urls')),
    path('api/', include('quantable_app.urls')),
]



