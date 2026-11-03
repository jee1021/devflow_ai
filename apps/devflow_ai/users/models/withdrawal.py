from datetime import date,timedelta
from django.conf import settings
from django.db import models


def default_due_date():
    return date.today() + timedelta(days=15)


class Withdrawal(models.Model):

    class Reason(models.TextChoices):
        ETC = "ETC","기타"
        NOT_SATISFIED = "NOT_SATISFIED", "불만족"

    class Status(models.TextChoices):
        PENDING = "PENDING", "탈퇴 대기"
        COMPLETED = "COMPLETED", "탈퇴 완료"
        CANCELED = "CANCELED", "탈퇴 취소"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="withdrawal",
    )
    reason = models.CharField(
        max_length=300,
        choices=Reason.choices
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason_detail = models.TextField()
    due_date = models.DateField(default=default_due_date)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "withdrawal"

    def __str__(self):
        return f"{self.user.email}-{self.get_reason_display()}"

    