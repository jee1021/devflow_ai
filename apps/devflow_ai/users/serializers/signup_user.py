from rest_framework import serializers
from apps.devflow_ai.users.models.signup_user import SignupUser

class SignupUserSerializer(serializers.ModelSerializer):
    password = serializers.ModelSerializer(write_only=True,max_length=13,min_length=7)
    password_confirm = serializers.ModelSerializer(write_only=True,max_length=13,min_length=7)



    class Meta:
        model = SignupUser
        fields = [
            "name",
            "email",
            "username",
            "username_confirm",
            "user_nickname",
            "password",
            "password_confirm"
            "birth_date",
            "phone_number",
            "user_profile",
            "user_position",
            "is_active"
        ]
        extra_kwargs = {
            "password" : {"write_only": True},
        }





