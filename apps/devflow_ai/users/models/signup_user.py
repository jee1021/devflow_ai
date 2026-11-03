from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from apps.devflow_ai.users.manager.user_manager import DevUserManager
class SignupUser(AbstractBaseUser,PermissionsMixin):

    class UserProfile(models.TextChoices):
        JUNIOR = "JUNIOR", "주니어"
        MIDDLE = "MIDDLE" , "미들"
        SENIOR = "SENIOR" , "시니어"

    class UserPosition(models.TextChoices):
        BACKEND_ENGINEER = "BACKEND_ENGINEER", "백엔드 엔지니어"
        FRONTEND_ENGINEER = "FRONTEND_ENGINEER", "프론트엔드 엔지니어"
        FULLSTACK_ENGINEER = "FULLSTACK_ENGINEER", "풀스텍 엔지니어"
        UXUI_DESIGNER = "UXUI_DESIGNER", "UX/UI 디자이너"
        BUSINESS_ANALYST = "BUSINESS_ANALYST", "비즈니스 분석가"
        PROJECT_MANAGER = "PROJECT_MANAGER", "프로젝트 매니저"
        CEO = "CEO", "창업자 대표"
        ASPIRING_JUNIOR = "ASPIRING_JUNIOR", "예비 개발 주니어"

    name = models.CharField(max_length=25,null=True,blank=True,verbose_name="실명")
    username = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        unique=True,
        validators=[MinLengthValidator(7),
                    RegexValidator(
                        regex=r'^[\w!@#$%^&*()\-+=]{4,20}$',
                        message="영문,숫자,특수문자 허용됩니다.",
                    ),
        ],
        error_messages={'unique': '이미 사용 중인 사용자명입니다.'},
    )
    username_confirm = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        unique=True,
        validators=[MinLengthValidator(7),
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
        validators=[MinLengthValidator(7),
                    RegexValidator(
                        regex=r'^[\w!@#$%^&*()\-+=]{4,20}$',
                        message="영문,숫자,특수문자 허용됩니다.",
                    ),
        ],
        error_messages={'unique': '이미 사용 중인 사용자닉네임입니다.'},
    )
    user_nickname_confirm = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        unique=True,
        validators=[MinLengthValidator(7),
                    RegexValidator(
                        regex=r'^[\w!@#$%^&*()\-+=]{4,20}$',
                        message="영문,숫자,특수문자 허용됩니다.",
                    ),
                    ],
        error_messages={'unique': '이미 사용 중인 사용자닉네임입니다.'},
    )
    email = models.EmailField(verbose_name="이메일")
    birth_date = models.DateField(null=True, blank=True, db_index=True, verbose_name="생년월일")
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
    user_profile = models.CharField(
        max_length=30,
        choices=UserProfile.choices,
        null=True,
        blank=True,
        verbose_name="사용자 경력"
    )
    user_position = models.CharField(
        max_length=30,
        choices=UserPosition.choices,
        null=True,
        blank=True,
        verbose_name="사용자 프로필"
    )
    agree_third_party = models.BooleanField(
        default=False,
        verbose_name="제3자 정보제공 동의",
    )
    groups = models.ManyToManyField(
        Group,
        related_name="signupuser_set",
        related_query_name="signupuser",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="signupuser_permissions_set",
        related_query_name="signupuser",
        blank=True,
    )


    is_active = models.BooleanField(default=True,verbose_name="활성 여부")
    is_staff = models.BooleanField(default=False,verbose_name="관리자여부")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="수정일시")
    phone_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="휴대폰인증일시")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = '유저'
        verbose_name_plural = '유저 회원가입'
        ordering = ['-created_at']

        # ===== 여기서 Unique 제약 조건을 한 번에 관리 =====
        constraints = [
            models.UniqueConstraint(fields=['email'], name='uniq_user_email'),
            models.UniqueConstraint(fields=['username'], name='uniq_user_username'),
            models.UniqueConstraint(fields=['user_nickname'], name='uniq_user_nickname'),
            models.UniqueConstraint(fields=['phone_number'], name='uniq_user_phone_number'),
        ]
    objects = DevUserManager()

    def __str__(self):
        return f"{self.username}{self.email}"
