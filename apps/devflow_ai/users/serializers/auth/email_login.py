from rest_framework import serializers

from apps.devflow_ai.users.models import SignupUser


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        model = SignupUser
        fields = ["email"]