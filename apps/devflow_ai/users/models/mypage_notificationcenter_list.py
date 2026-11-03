from django.conf import settings
from django.db import models
from django.utils import timezone
from typing import Any

from apps.devflow_ai.users.manager.mypage_notificationCenter_list_manager import MyPageNotificationCenterListManager
from apps.devflow_ai.users.models.notificationtype import NotificationType
from apps.devflow_ai.users.models.mypage_notificationCenter_user import MyPageNotificationCenterUser


class MyPageNotificationCenterList(models.Model):

    class MyPageNotification(models.TextChoices):
        PR_REVIEW = "PR_REVIEW", "PR_리뷰"
        CODE_REFACTORING = "CODE_REFACTORING", "코드 리펙토링"
        MEETING_NOTICE = "MEETING_NOTICE", "미팅회의 공지알림"
        MAINTENANCE = "MAINTENANCE", "유지보수 알림"
        PR_APPROVED = "PR_APPROVED", "PR 승인 알림"
        PR_REJECTED = "PR_REJECTED", "PR 승인 거절 알림"
        MENTION = "MENTION", "멘션 알림"

    class MyPageNotification_Status(models.TextChoices):
        NONE = "NONE", "해당없음"
        PENDING = "PENDING", "대기중"
        APPROVED = "APPROVED", "승인"
        REJECTED = "REJECTED", "거절"

    REQUEST_TYPES = [
        MyPageNotification.MAINTENANCE,
        MyPageNotification.PR_APPROVED,
        MyPageNotification.PR_REJECTED,
    ]  # 승인/거절 절차가 필요한 알림 타입 목록 — 실제 정책에 맞게 조정하세요

    center = models.ForeignKey(
        MyPageNotificationCenterUser,
        on_delete=models.CASCADE,
    )
    mypage_notification = models.CharField(
        max_length=30,
        choices=MyPageNotification.choices,
        null=True,
        blank=True,
        verbose_name="알림센터신청리스트",
    )
    mypage_notification_Status = models.CharField(
        max_length=30,
        choices=MyPageNotification_Status.choices,
        null=True,
        blank=True,
        verbose_name="알림센터신청상태",
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.PROTECT,
        verbose_name="알림 종류",
    )
    title = models.CharField(max_length=255, verbose_name="제목")
    message = models.TextField(blank=True, verbose_name="내용")
    is_read = models.BooleanField(default=False, verbose_name="읽음 여부")
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_notifications",
        verbose_name="처리자",
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="처리일시")
    reject_reason = models.TextField(blank=True, verbose_name="거절 사유")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    objects = MyPageNotificationCenterListManager()

    class Meta:
        verbose_name = "알림 센터"
        verbose_name_plural = "알림 센터 리스트"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["center", "is_read"]),
            models.Index(fields=["mypage_notification_Status"]),
        ]

    def __str__(self):
        return f"[{self.notification_type.label}] {self.title} ({self.center})"

    def save(self, *args: Any, **kwargs: Any):
        if (
            self.notification_type in self.REQUEST_TYPES
            and self.mypage_notification_Status == self.MyPageNotification_Status.NONE
            and self._state.adding
        ):
            self.mypage_notification_Status = self.MyPageNotification_Status.PENDING
        super().save(*args, **kwargs)

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])

    def approve(self, processed_by=None):
        if self.mypage_notification_Status != self.MyPageNotification_Status.PENDING:
            raise ValueError("대기중 상태인 신청만 승인할 수 있습니다.")
        self.mypage_notification_Status = self.MyPageNotification_Status.APPROVED
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.save(update_fields=["mypage_notification_Status", "processed_by", "processed_at"])

    def reject(self, processed_by=None, reason=""):
        if self.mypage_notification_Status != self.MyPageNotification_Status.PENDING:
            raise ValueError("대기중 상태인 신청만 거절할 수 있습니다.")
        self.mypage_notification_Status = self.MyPageNotification_Status.REJECTED
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.reject_reason = reason
        self.save(update_fields=["mypage_notification_Status", "processed_by", "processed_at", "reject_reason"])

    @property
    def is_request(self):
        return self.notification_type in self.REQUEST_TYPES

    @property
    def is_pending(self):
        return self.mypage_notification_Status == self.MyPageNotification_Status.PENDING