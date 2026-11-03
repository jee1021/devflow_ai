from django.db import models
from apps.devflow_ai.users.models.mypage_notificationCenter_user import MyPageNotificationCenterUser

class MyPageNotificationSetting(models.Model):
    center = models.OneToOneField(
        MyPageNotificationCenterUser,
        on_delete=models.CASCADE,
        related_name="notification_setting"
    )
    pr_review = models.BooleanField(default=True,verbose_name="PR리뷰알림")
    code_refactoring = models.BooleanField(default=True,verbose_name="코드리팩토림알림")
    maintenance = models.BooleanField(default=True, verbose_name="유지보수 신청 알림")
    pr_approved = models.BooleanField(default=True, verbose_name="PR 승인 알림")
    pr_rejected = models.BooleanField(default=False, verbose_name="PR 승인 거절 알림")
    mention = models.BooleanField(default=True, verbose_name="멘션 알림")

    class Meta:
        verbose_name = "알림 설정"
        verbose_name_plural = "알림 설정 리스트"
    def __str__(self):
        return f"{self.center}의 알림 설정"

    def is_enabled(self, notification_type: str) -> bool:
        return getattr(self, notification_type, False)