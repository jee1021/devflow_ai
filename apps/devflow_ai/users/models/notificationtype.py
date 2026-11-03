from django.db import models


class NotificationType(models.Model):
    """
    알림 종류를 관리하는 마스터 테이블.
    새로운 알림 종류가 추가되어도 코드 배포 없이 데이터만 추가하면 됩니다.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="알림 코드",
        help_text="pr_review, mention 처럼 코드 내부에서 참조할 고유 식별자",
    )
    label = models.CharField(
        max_length=100,
        verbose_name="알림 이름",
        help_text="유저에게 노출되는 이름 (예: PR 리뷰 알림)",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="설명",
    )
    default_enabled = models.BooleanField(
        default=True,
        verbose_name="기본 활성화 여부",
        help_text="새 유저 생성 시 이 알림의 기본값",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="사용 여부",
        help_text="비활성화하면 마이페이지 알림센터에서 노출되지 않음",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="정렬 순서",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "알림 종류"
        verbose_name_plural = "알림 종류"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label} ({self.code})"