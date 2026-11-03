from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError


class DevUserManager(BaseUserManager):
    def create_user(self, email, username, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        if not username:
            raise ValueError('사용자 아이디는 필수입니다.')
        if not phone_number:
            raise ValueError('휴대폰 번호는 필수입니다.')
        if not password:
            raise ValueError('비밀번호는 필수입니다.')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff는 True여야 합니다.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser는 True여야 합니다.')

        return self.create_user(email, username, phone_number, password, **extra_fields)