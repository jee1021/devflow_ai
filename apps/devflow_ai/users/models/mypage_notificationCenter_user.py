from django.db import models
from apps.devflow_ai.users.models import SignupUser


class MyPageNotificationCenterUser(models.Model):
    user = models.OneToOneField(
        SignupUser,
        on_delete=models.CASCADE,
    )

    pr_review = models.BooleanField(
        default=True,
        verbose_name ="pr_리뷰 알림"
    )
    code_refactoring = models.BooleanField(
        default=True,
        verbose_name="코드 리펙토링 알림"
    )
    meeting_notice = models.BooleanField(
        default=True,
        verbose_name="회의 공지 알림"
    )
    maintenance = models.BooleanField(
        default=True,
        verbose_name="유지보수 신청알림"
    )
    pr_approved  = models.BooleanField(
        default=True,
        verbose_name="PR승인알림"
    )
    pr_rejected = models.BooleanField(
        default=False,
        verbose_name="PR 승인거절알림"
    )
    mention = models.BooleanField(
        default=True,
        verbose_name="맨션알림"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "알림 센터"
        verbose_name_plural = "알림 센터"

    def __str__(self):
        return f"{self.user.username}알림센터"

