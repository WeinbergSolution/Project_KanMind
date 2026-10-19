from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .serializers import RegistrationSerializer

from rest_framework.authtoken.models import Token

from rest_framework.response import Response
from rest_framework import status


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            "token": token.key,
            "fullname": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "user_id": user.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
