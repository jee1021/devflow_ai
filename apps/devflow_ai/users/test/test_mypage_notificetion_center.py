from http import HTTPStatus
from unittest.mock import patch
import pytest
from rest_framework.test import APIClient

from apps.devflow_ai.users.models import SignupUser
from apps.devflow_ai.users.models.mypage_notificationCenter_user import (
    MyPageNotificationCenterUser,
)

MYPAGE_NOTIFICATIONCENTER_URL = "/api/v1/users/mypage_notification_center"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def payload():
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
            "email": "suning@example.com",
        }
        payload.update(overrides)
        return payload
    return _make_payload


@pytest.fixture
def auth_client(api_client, django_user_model):
    user = django_user_model.objects.create_user(
        username="username_we@@",
        email="tester@example.com",
        phone_number="01012345678",
        password="test_password124@@",
    )
    api_client.force_login(user)  # force_authenticate -> force_login
    api_client.user = user  # 테스트에서 이 유저로 알림센터 row를 만들기 위해 보관
    return api_client


@pytest.mark.django_db
def test_mypage_notification_center_unauthorized(api_client):
    """비로그인 -> 401"""
    response = api_client.get(MYPAGE_NOTIFICATIONCENTER_URL)

    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "로그인이 필요합니다."


@pytest.mark.django_db
def test_mypage_notification_center_not_found_fails(api_client, payload):
    """로그인했지만 알림센터가 없는 유저 -> 404"""
    data = payload()
    data.pop("username_confirm")
    data.pop("password_confirm")
    user = SignupUser.objects.create_user(**data)

    api_client.force_login(user)  # force_authenticate -> force_login
    response = api_client.get(MYPAGE_NOTIFICATIONCENTER_URL,data=payload(), format="json")


    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "알림이 존재하지 않습니다."


@pytest.mark.django_db
def test_mypage_notification_center_success(api_client, payload, auth_client):
    MyPageNotificationCenterUser.objects.create(user=auth_client.user)

    response = auth_client.get(MYPAGE_NOTIFICATIONCENTER_URL,data=payload(), format="json")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "조회에 성공!!"