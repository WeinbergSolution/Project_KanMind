from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("kanban_App.api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("auth_App.api.urls")),
]
