from rest_framework import serializers

from apps.devflow_ai.users.models import Withdrawal


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = "__all__"