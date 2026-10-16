from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Validate credentials and resolve them to the autenticated User
    """

    def validate(self, data):
        """Autheticate by Emal and passwort"""
