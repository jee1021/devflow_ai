from django.db import models
from apps.devflow_ai.users.models.mypage_notification_setting import (
    MyPageNotificationSetting,
)


class MyPageNotificationCenterListQuerySet(models.QuerySet):
    def unread(self):
        return self.filter(is_read=False)

    def pending(self):
        return self.filter(
            mypage_notification_Status=self.model.MyPageNotification_Status.PENDING
        )

    def for_center(self, center):
        return self.filter(center=center)


class MyPageNotificationCenterListManager(models.Manager):
    def get_queryset(self):
        return MyPageNotificationCenterListQuerySet(self.model, using=self._db)

    def unread(self):
        return self.get_queryset().unread()

    def pending(self):
        return self.get_queryset().pending()

    def notify(self, center, notification_type, title, message=""):
        """단순 알림 생성 (설정이 꺼져 있으면 생성하지 않음)"""

        setting, _ = MyPageNotificationSetting.objects.get_or_create(center=center)
        if not setting.is_enabled(notification_type):
            return None

        return self.create(
            center=center,
            notification_type=notification_type,
            title=title,
            message=message,
        )

    def request(self, center, notification_type, title, message=""):
        """승인/거절이 필요한 신청 생성 (예: 유지보수 신청)"""

        setting, _ = MyPageNotificationSetting.objects.get_or_create(center=center)
        if not setting.is_enabled(notification_type):
            return None

        return self.create(
            center=center,
            notification_type=notification_type,
            title=title,
            message=message,
            mypage_notification_Status=self.model.MyPageNotification_Status.PENDING,
        )