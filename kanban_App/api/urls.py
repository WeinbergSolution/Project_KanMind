from django.urls import path, include
from rest_framework import routers
from .views import BoardViewSet, TaskViewSet

router = routers.SimpleRouter()
router.register(r"boards", BoardViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
