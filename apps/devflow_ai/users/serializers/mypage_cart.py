from rest_framework import serializers
from apps.devflow_ai.users.models.mypage_cart import MyPageCart

class MyPageCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPageCart
        fields = '__all__'\
