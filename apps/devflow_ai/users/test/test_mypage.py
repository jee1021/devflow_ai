

import pytest
from rest_framework.test import APIClient
from django.db import IntegrityError
from apps.devflow_ai.users.models.signup_user import SignupUser

MYPAGE_URL = "/api/v1/users/mypage"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def login_user_mypage():
    user = SignupUser(
        username="username_we@@",
        user_nickname="test_nick",
        user_position="BACKEND_ENGINEER",
        user_profile="JUNIOR",
    )
    user.set_password("test_password124@@")
    user.save()
    return user


@pytest.fixture
def make_payload():
    def _make_payload(**overrides):
        payload = {
            "username": "username_we@@",
            "username_confirm": "username_we@@",
            "password": "test_password124@@",
            "password_confirm": "test_password124@@",
            "user_nickname": "test_nick",
            "user_position": "BACKEND_ENGINEER",
            "user_profile": "JUNIOR",
            "phone_number": "01012345678",
        }
        payload.update(overrides)
        return payload
    return _make_payload


@pytest.mark.django_db
def test_login_user_mypage_login_false(api_client, login_user_mypage, make_payload):
    payload = make_payload()
    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "로그인이 필요합니다."


@pytest.mark.django_db
def test_payload_schema_rejects_mismatched_username_confirmation(api_client, login_user_mypage, make_payload):
    api_client.force_login(login_user_mypage)  # 로그인 처리 추가

    payload = make_payload(
        username="username_we",
        username_confirm="username_we@@",  # 일부러 다르게 (payload.username과 다름)
    )
    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "사용자 아이디가 일치 하지않습니다."

@pytest.mark.django_db
def test_payload_schema_rejects_mismatched_password_confirmation(api_client, login_user_mypage, make_payload):
    api_client.force_login(login_user_mypage)  # 로그인 처리 추가

    payload = make_payload(
        password="test_password124@@",
        password_confirm="test_password124@",  # 일부러 다르게 (payload.password와 다름)
    )
    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "비밀번호가 일치 하지않습니다."


@pytest.mark.django_db
def test_login_user_mypage_success(api_client, login_user_mypage, make_payload):

    api_client.force_login(login_user_mypage)  # 로그인 처리 추가

    payload = make_payload()
    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "마이페이지 정보 수정을 성공했습니다."


@pytest.mark.django_db
def test_mypage_login_user_not_found(api_client, login_user_mypage, make_payload, mocker):
    api_client.force_login(login_user_mypage)

    original_get = SignupUser.objects.get

    def fake_get(*args, **kwargs):
        if "username" in kwargs:
            raise SignupUser.DoesNotExist
        return original_get(*args, **kwargs)

    mocker.patch(
        "apps.devflow_ai.users.account.router.mypage.SignupUser.objects.get",
        side_effect=fake_get,
    )

    payload = make_payload()
    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "유저를 찾을 수 없습니다."



@pytest.mark.django_db
def test_mypage_login_user_IntegrityError(api_client, login_user_mypage, make_payload, mocker):
    api_client.force_login(login_user_mypage)

    original_get = SignupUser.objects.get

    def fake_get(*args, **kwargs):
        if "username" in kwargs:
            raise IntegrityError
        return original_get(*args, **kwargs)

    mocker.patch(
        "apps.devflow_ai.users.account.router.mypage.SignupUser.objects.get",
        side_effect=fake_get,
    )
    payload = make_payload()
    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 409
    assert response.json()["success"] is False
    assert response.json()["message"] == "이미 사용 중인 정보가 있습니다."

@pytest.mark.django_db
def test_mypage_fails(api_client, login_user_mypage, make_payload, mocker):
    api_client.force_login(login_user_mypage)

    # objects.get 대신 DB 업데이트/저장 과정에서 예외가 나도록 패치
    mocker.patch.object(
        SignupUser,
        "save",
        side_effect=Exception("DB Save Error")
    )

    payload = make_payload(
        username="username_we@@",
        username_confirm="username_we@@",
        password="test_password124@@",
        password_confirm="test_password124@@",
        user_position="BACKEND_ENGINEER",
        user_profile="JUNIOR",
    )

    response = api_client.patch(MYPAGE_URL, data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "수정에 실패했습니다."

