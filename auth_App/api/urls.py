from django.urls import path
from .views import RegistrationView, LoginView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("registration/", RegistrationView.as_view()),
]
