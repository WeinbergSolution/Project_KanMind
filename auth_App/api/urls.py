from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegistrationView

urlpatterns = [
    path("login/", obtain_auth_token),
    path("registration/", RegistrationView.as_view()),
]
