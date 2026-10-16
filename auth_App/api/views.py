from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import LoginSerializer


class RegistrationView(generics.CreateAPIView):

    pass
