from django.db import models

from apps.devflow_ai.users.models import SignupUser
from apps.devflow_ai.users.models.notificationtype import NotificationType


class UserNotificationSetting(models.Model):
    """
    유저별 알림 on/off 설정.
    (user, notification_type) 조합은 유일해야 함.
    """

    user = models.ForeignKey(
        SignupUser,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name="user_settings",
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name="알림 수신 여부",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "유저 알림 설정"
        verbose_name_plural = "유저 알림 설정"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "notification_type"],
                name="unique_user_notification_type",
            )
        ]
        indexes = [
            models.Index(fields=["user", "notification_type"]),
        ]

    def __str__(self):
        status = "ON" if self.enabled else "OFF"
        return f"{self.user.username} - {self.notification_type.label} ({status})"
