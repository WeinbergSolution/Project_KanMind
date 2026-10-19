from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )

        return attrs

    def validate_email(self, value):
        is_user = User.objects.filter(email=value).exists()

        if is_user:
            raise serializers.ValidationError("Email address already in use.")

        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        first_name, last_name = self.split_fullname(validated_data["fullname"])

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        return user

    def split_fullname(self, fullname):
        name_parts = fullname.split(" ", 1)
        first_name = name_parts[0]

        if len(name_parts) >= 2:
            last_name = name_parts[1]
        else:
            last_name = ""

        return first_name, last_name


class LoginSerializer(serializers.Serializer):
    """
    Validate credentials and resolve them to the authenticated user.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate by email and password."""
        email = data["email"]
        password = data["password"]
        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        data["user"] = user
        return data
