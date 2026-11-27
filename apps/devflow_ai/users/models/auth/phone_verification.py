from django.core.validators import RegexValidator
from django.db import models
from datetime import timedelta
from django.utils import timezone
class PhoneVerification(models.Model):

    phone_number = models.CharField(
        max_length=20,
        verbose_name="전화번호",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="올바른 전화번호 형식을 입력해주세요. (예: 01012345678 또는 +821012345678)",
            )
        ]
    )
    code = models.CharField(max_length=6, verbose_name="인증번호")
    is_verified = models.BooleanField(default=False, verbose_name="인증 완료 여부")
    is_used = models.BooleanField(default=False, verbose_name="가입에 사용됨 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="인증 완료일시")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="만료일시")

    class Meta:
        verbose_name = "휴대폰 인증"
        verbose_name_plural = "휴대폰 인증내역"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number}({self.code})"

    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    def save(self, *args, **kwargs):
        # 최초 생성 시 만료시간 5분으로 자동 설정
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
