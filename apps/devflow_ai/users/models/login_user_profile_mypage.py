from django.core.validators import RegexValidator, MinLengthValidator
from django.db import models

from apps.devflow_ai.users.models import SignupUser



class LoginUserProfileMyPage(models.Model):

    class UserPosition(models.TextChoices):
        BACKEND_ENGINEER = "BACKEND_ENGINEER", "백엔드 엔지니어"
        FRONTEND_ENGINEER = "FRONTEND_ENGINEER", "프론트엔드 엔지니어"
        FULLSTACK_ENGINEER = "FULLSTACK_ENGINEER", "풀스텍 엔지니어"
        UXUI_DESIGNER = "UXUI_DESIGNER", "UX/UI 디자이너"
        BUSINESS_ANALYST = "BUSINESS_ANALYST", "비즈니스 분석가"
        PROJECT_MANAGER = "PROJECT_MANAGER", "프로젝트 매니저"
        CEO = "CEO", "창업자 대표"
        OTHER = "OTHER", "기타"
    class UserProfile(models.TextChoices):
        JUNIOR = "JUNIOR", "주니어"
        MIDDLE = "MIDDLE" , "미들"
        SENIOR = "SENIOR" , "시니어"

    user = models.OneToOneField(
        SignupUser,
        on_delete=models.CASCADE,
        related_name="profile_info"
    )
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
    user_position = models.CharField(
        max_length=20,
        choices=UserPosition.choices,
        null=True,
        blank=True,
        verbose_name="사용자 포지션"
    )

    user_profile = models.CharField(
        max_length=20,
        choices=UserProfile.choices,
        null=True,
        blank=True,
        verbose_name="사용자 프로필"
    )
    username = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                regex=r'^[\w!@#$%^&*()\-+=]{4,20}$',
                message="영문,숫자,특수문자 허용됩니다.",
            ),
        ],
        error_messages={'unique': '이미 사용 중인 사용자명입니다.'},
    )
    user_nickname = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        unique=True,
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                regex=r'^[\w!@#$%^&*()\-+=]{4,20}$',
                message="영문,숫자,특수문자 허용됩니다.",
            ),
        ],
        error_messages={'unique': '이미 사용 중인 사용자닉네임입니다.'},
    )

    # 로그인 정보
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="마지막 로그인 IP")
    login_count = models.PositiveIntegerField(default=0, verbose_name="로그인 횟수")

    class Meta:
        verbose_name = "유저 추가 정보"
        verbose_name_plural = "유저 추가 정보"

    def __str__(self):
        return f"{self.user.username} 추가 정보"