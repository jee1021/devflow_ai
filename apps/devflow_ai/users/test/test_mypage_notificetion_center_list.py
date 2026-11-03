import pytest
from rest_framework.test import APIClient

from apps.devflow_ai.users.models import SignupUser
from apps.devflow_ai.users.models.mypage_notificationcenter_list import MyPageNotificationCenterList

MYPAGE_NOTIFICATION_CENTER_LIST_URL = "/api/v1/users/mypage_notification_center_list"

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
            "mypage_notification": "PR_REVIEW",
            "title": "pr_review",
            "message": "pr_review post",
        }
        payload.update(overrides)
        return payload
    return _make_payload

@pytest.mark.django_db
def test_mypage_login_user_fails(api_client, make_payload):
    payload = make_payload()
    response = api_client.post(MYPAGE_NOTIFICATION_CENTER_LIST_URL, data=payload, format="json")
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "로그인이 필요합니다."

@pytest.mark.django_db
def test_mypage_notification_is_none(
    api_client,
    make_payload,
    login_user_mypage,
):
    api_client.force_login(login_user_mypage)

    payload = make_payload(
        mypage_notification=None,
        mypage_notification_status=True,
        # " "가 아니라 None
        title="pr_review",
    )

    response = api_client.post(
        MYPAGE_NOTIFICATION_CENTER_LIST_URL,
        data=payload,
        format="json",
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] =="마이페이지(MyPageNotification)알림신청을 선택해주세요"


@pytest.mark.django_db
def test_mypage_notification_status_is_none(
    api_client,
    make_payload,
    login_user_mypage,
):
    api_client.force_login(login_user_mypage)

    payload = make_payload(
        MyPageNotification="PR_REVIEW",
        MyPageNotification_Status=None,
        title="pr_review",
    )
    response = api_client.post(
        MYPAGE_NOTIFICATION_CENTER_LIST_URL,
        data=payload,
        format="json",
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "마이페이지(MyPageNotification_Status)를 알림신청상태를 선택해주세요"



