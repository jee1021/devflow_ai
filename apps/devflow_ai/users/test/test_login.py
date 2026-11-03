import pytest

from rest_framework.test import APIClient
from apps.devflow_ai.users.models.signup_user import SignupUser

LOGIN_URL = "/api/v1/users/login"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def login_user():
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
            "password": "test_password124@@",
            "user_nickname": "test_nick",
            "user_position": "BACKEND_ENGINEER",
            "user_profile": "JUNIOR",
        }
        payload.update(overrides)
        return payload
    return _make_payload

@pytest.mark.django_db
def test_login_fail_when_username_missing(api_client, make_payload):
    payload = make_payload(
        username=" ",
        user_nickname="test_nick",
        user_position="BACKEND_ENGINEER",
        password="test_password124@@",
        user_profile="JUNIOR",
    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "아이디를 입력해주세요."


@pytest.mark.django_db
def test_login_fall_when_password_missing(api_client, make_payload):
    payload = make_payload(
        username="username_we@@",
        user_nickname="test_nick",
        user_position="BACKEND_ENGINEER",
        user_profile="JUNIOR",
        password=" ",
    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "비밀번호를 입력해주세요."


@pytest.mark.django_db
def test_login_fall_when_user_nickname_missing(api_client, make_payload):
    payload = make_payload(
        username="username_we@@",
        user_nickname=" ",
        user_position="BACKEND_ENGINEER",
        user_profile="JUNIOR",
        password="test_password124@@",
    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "닉네임을 입력해주세요."


@pytest.mark.django_db
def test_user_profile_check(api_client, make_payload):
    payload = make_payload(
        username="username_we@@",
        user_nickname="test_nick",
        user_position="BACKEND_ENGINEER",
        user_profile=" ",
        password="test_password124@@",

    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "경력(user_profile)을 선택해주세요."

@pytest.mark.django_db
def test_user_position_check(api_client, make_payload):
    payload = make_payload(
        username="username_we@@",
        user_nickname="test_nick",
        user_position=" ",
        user_profile="JUNIOR",
        password="test_password124@@",
    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "직군(user_position)을 선택해주세요."


@pytest.mark.django_db
def test_user_username_missmatch(api_client, make_payload):

    payload = make_payload(
        username="loveme@@",
    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "아이디가 일치하지 않습니다."

@pytest.mark.django_db
def test_user_user_inckname_missmatch(api_client, make_payload):
    SignupUser.objects.create(
        username="username_we@@",
        user_nickname="real_nick",        # payload 기본값과 다른 값
        user_position="BACKEND_ENGINEER",
        user_profile="JUNIOR",
    )
    payload = make_payload(
        user_nickname="real_nick@@",
    )
    response = api_client.post(LOGIN_URL,data=payload, format="json")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "닉네임이 일치하지 않습니다."

@pytest.mark.django_db
def test_user_user_password_mismatch(api_client, make_payload):
    user = SignupUser.objects.create(
        username="username_we@@",
        user_nickname="test_nick",
        user_position="BACKEND_ENGINEER",
        user_profile="JUNIOR",
    )
    user.set_password("test_password124@@")
    user.save()

    payload = make_payload(
        password="test@1234",
    )
    response = api_client.post(LOGIN_URL, data=payload, format="json")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "비밀번호가 일치하지 않습니다."


@pytest.mark.django_db
def test_user_user_position_mismatch(api_client, make_payload,login_user):
    payload = make_payload(user_position="FRONTEND_ENGINEER")

    response = api_client.post(LOGIN_URL, data=payload, format="json")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] ==  "직군정보가 일치하지 않습니다."


@pytest.mark.django_db
def test_user_login_fails_when_system_error(api_client, make_payload,login_user,mocker):

    mocker.patch.object(
        SignupUser,
        "check_password",
        side_effect=RuntimeError("boom")

    )
    payload = make_payload()
    response = api_client.post(LOGIN_URL, data=payload, format="json")
    assert response.status_code == 500
    assert response.json()["success"] is False
    assert response.json()["message"] == "로그인 시도중 시스템 에러가 발생했습니다."


@pytest.mark.django_db
def test_user_login_success(api_client, make_payload,login_user):
    payload = make_payload(
        username="username_we@@",
        user_nickname="test_nick",
        user_position="BACKEND_ENGINEER",
    )
    response = api_client.post(LOGIN_URL, data=payload, format="json")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "devflow_ai 로그인 성공!!"