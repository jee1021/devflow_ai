from rest_framework import serializers

from apps.devflow_ai.users.models import SignupUser


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    class Meta:
        model = SignupUser
        fields = [
            "username",
            "user_nickname",
            "user_profile",
            "user_position",

        ]
        extra_kwargs = {
            "password" : {"write_only": True},
        }