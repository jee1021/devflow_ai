from typing import Any

import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError
from apps.devflow_ai.users.models import SignupUser
from apps.devflow_ai.users.models.phone_verification import PhoneVerification

SIGNUP_URL = "/api/v1/users/signup"
CHECK_EMAIL_URL = f"{SIGNUP_URL}/check-email"
CHECK_USERNAME_URL = f"{SIGNUP_URL}/check-username"
CHECK_NICKNAME_URL = f"{SIGNUP_URL}/check-nickname"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_payload():
    def _make_payload(**overrides: Any) -> Any:
        payload = {
            "name": "test_name",
            "username": "username_we@@",
            "username_confirm": "username_we@@",
            "email": "suning@example.com",
            "password": "test_password124@@",
            "password_confirm": "test_password124@@",
            "phone_number": "010-1234-56789",
            "birth_date": "1990-01-01",
            "user_profile": "JUNIOR",
            "user_position": "BACKEND_ENGINEER",
            "user_nickname": "test_nick",
            "phone_verification_code": "123456",
            "agree_third_party": True,
        }
        payload.update(overrides)
        return payload
    return _make_payload


# =====================================================================
# 회원가입 (기존 테스트)
# =====================================================================
@pytest.mark.django_db
def test_username_mismatch(api_client, make_payload):

    payload = make_payload(
        username="username_we@@",
        username_confirm="different1",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format='json')
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "사용자 아이디가 일치 하지않습니다."


@pytest.mark.django_db
def test_duplicate_username(api_client, make_payload):
    SignupUser.objects.create(
        username="username_we@@",
        username_confirm="username_we@@",
        email="suning@example.com",
        phone_number="010-1234-56789",
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        email="other@example.com",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format='json')
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "이미 사용중인 아이디 입니다."


@pytest.mark.django_db
def test_duplicate_email_check(api_client, make_payload):
    SignupUser.objects.create(
        username="username_we@@",
        email="suning@example.com",
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        email="suning@example.com",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format='json')
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "이미 가입된 이메일입니다."


@pytest.mark.django_db
def test_phone_number_check(api_client, make_payload):
    SignupUser.objects.create(
        phone_number="010-1234-56789",
    )
    payload = make_payload(
        phone_number="010-1234-56789",
        phone_verification_code="123456",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format='json')
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "이미 가입된 휴대폰입니다."


@pytest.mark.django_db
def test_phone_verification_required(api_client, make_payload):
    payload = make_payload(
        username="username1",
        username_confirm="username1",
        phone_number="010-1234-5678",
        phone_verification_code="123456",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 409
    assert response.json()["success"] is False
    assert response.json()["message"] == "휴대폰 인증 센터에서 1차 검증후 가입서를 작성해주세요."


@pytest.mark.django_db
def test_phone_verification_expired(api_client, make_payload):
    # 인증은 됐지만 만료된 경우
    PhoneVerification.objects.create(
        phone_number="010-9999-9999",
        code="123456",
        is_verified=True,
        is_used=False,
        expires_at=timezone.now() - timedelta(minutes=1),
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        phone_number="010-9999-9999",
        phone_verification_code="123456",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 409
    assert response.json()["success"] is False
    assert response.json()["message"] == "휴대폰 인증 센터에서 1차 검증후 가입서를 작성해주세요."


@pytest.mark.django_db
def test_agree_third_party_check(api_client, make_payload):
    PhoneVerification.objects.create(
        phone_number="010-1234-5678",
        code="123456",
        is_verified=True,
        is_used=False,
        expires_at=timezone.now() + timedelta(minutes=10),  # 반드시 미래 시간
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        phone_number="010-1234-5678",
        phone_verification_code="123456",
        agree_third_party=False,
    )
    response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 409
    assert response.json()["success"] is False
    assert response.json()["message"] == "제3자 정보제공 동의 체크후 가입서를 작성해주세요."


@pytest.mark.django_db
def test_user_position_check(api_client, make_payload):
    PhoneVerification.objects.create(
        phone_number="010-1234-5678",
        code="123456",
        is_verified=True,
        is_used=False,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        phone_number="010-1234-5678",
        phone_verification_code="123456",
        user_position=" ",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "직군(user_position)을 선택해주세요."


@pytest.mark.django_db
def test_user_profile_check(api_client, make_payload):
    PhoneVerification.objects.create(
        phone_number="010-1234-5678",
        code="123456",
        is_verified=True,
        is_used=False,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        phone_number="010-1234-5678",
        phone_verification_code="123456",
        user_profile=" ",
    )
    response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False

    assert response.json()["message"] == "경력(user_profile)을 선택해주세요."


@pytest.mark.django_db
def test_signup_returns_400_when_integrity_error_duplicate_user(api_client, make_payload):
    # 사전 중복 체크(username/email/phone)는 정상 통과시키고,
    # DB 저장 시점에 발생하는 IntegrityError(동시성 경합 등)만 별도로 검증한다.
    PhoneVerification.objects.create(
        phone_number="010-1234-5678",
        code="123456",
        is_verified=True,
        is_used=False,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        phone_number="010-1234-5678",
        phone_verification_code="123456",
    )
    with patch.object(SignupUser.objects, "create", side_effect=IntegrityError()):
        response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "이미 가입된 정보가 있습니다. 로그인해주세요"


@pytest.mark.django_db
def test_signup_success(api_client, make_payload):
    PhoneVerification.objects.create(
        phone_number="010-1234-5678",
        code="123456",
        is_verified=True,
        is_used=False,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        phone_number="010-1234-5678",
        phone_verification_code="123456",
        agree_third_party=True,
    )
    response = api_client.post(SIGNUP_URL, data=payload, format="json")
    assert response.status_code == 201
    assert SignupUser.objects.filter(username="username_we@@").exists()
    assert response.json()["success"] is True
    assert response.json()["message"] == "회원가입 성공!! 로그인 해주세요"


# =====================================================================
# 이메일 중복확인  GET /check-email?email=
# =====================================================================
@pytest.mark.django_db
def test_check_email_available(api_client):
    response = api_client.get(CHECK_EMAIL_URL, {"email": "new@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "사용 가능한 이메일입니다."
    assert response.json()["data"]["available"] is True


@pytest.mark.django_db
def test_check_email_duplicate(api_client):
    SignupUser.objects.create(
        username="username_we@@",
        email="suning@example.com",
    )
    response = api_client.get(CHECK_EMAIL_URL, {"email": "suning@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "이미 가입된 이메일입니다."
    assert response.json()["data"]["available"] is False


@pytest.mark.django_db
def test_check_email_blank(api_client):
    response = api_client.get(f"{CHECK_EMAIL_URL}?email=%20")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "이메일을 입력해주세요."


# =====================================================================
# 아이디 중복확인  GET /check-username?username=
# =====================================================================
@pytest.mark.django_db
def test_check_username_available(api_client):
    response = api_client.get(CHECK_USERNAME_URL, {"username": "brand_new1"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "사용 가능한 아이디입니다."
    assert response.json()["data"]["available"] is True


@pytest.mark.django_db
def test_check_username_duplicate(api_client):
    SignupUser.objects.create(
        username="username_we@@",
        email="suning@example.com",
    )
    response = api_client.get(CHECK_USERNAME_URL, {"username": "username_we@@"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "이미 사용중인 아이디입니다."
    assert response.json()["data"]["available"] is False


@pytest.mark.django_db
def test_check_username_blank(api_client):
    response = api_client.get(f"{CHECK_USERNAME_URL}?username=%20")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "아이디를 입력해주세요."


# =====================================================================
# 닉네임 중복확인  GET /check-nickname?nickname=
# =====================================================================
@pytest.mark.django_db
def test_check_nickname_available(api_client):
    response = api_client.get(CHECK_NICKNAME_URL, {"nickname": "brand_nick"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "사용 가능한 닉네임입니다."
    assert response.json()["data"]["available"] is True


@pytest.mark.django_db
def test_check_nickname_duplicate(api_client):
    SignupUser.objects.create(
        username="username_we@@",
        user_nickname="test_nick",
    )
    response = api_client.get(CHECK_NICKNAME_URL, {"nickname": "test_nick"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "이미 사용중인 닉네임입니다."
    assert response.json()["data"]["available"] is False


@pytest.mark.django_db
def test_check_nickname_blank(api_client):
    response = api_client.get(CHECK_NICKNAME_URL, {"nickname": ""})
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "닉네임을 입력해주세요."