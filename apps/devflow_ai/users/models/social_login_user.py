from django.db import models

from apps.devflow_ai.users.models.signup_user import SignupUser


class SocialUser(models.Model):
    class Provider(models.TextChoices):
        KAKAO = "KAKAO", "카카오"
        NAVER = "NAVER", "네이버"

    user = models.ForeignKey(
        SignupUser,
        on_delete=models.CASCADE,
        related_name="social_accounts",
        verbose_name="사용자",
    )
    provider = models.CharField(
        max_length=10,
        choices=Provider.choices,
        verbose_name="소셜 제공자",
    )
    provider_id = models.CharField(max_length=255, verbose_name="소셜 고유 ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "social_users"
        ordering = ["-created_at"]
        verbose_name = "소셜 계정"
        verbose_name_plural = "소셜 계정 목록"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_id"],
                name="unique_provider_account",  
            )
        ]
        indexes = [
            models.Index(fields=["provider", "provider_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.provider}"