import pytest
from rest_framework.test import APIClient
from apps.devflow_ai.users.models.signup_user import SignupUser

MYPAGEPASSWORDCHANGE_URL = "/api/v1/users/mypage_password_change"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def payload():
    def _make_payload(**overrides):
        payload = {
            "current_password": "test_password124@@",
            "new_change_password": "test_password125@@",
            "new_change_password_confirm": "test_password125@@",
        }
        payload.update(overrides)
        return payload
    return _make_payload

@pytest.mark.django_db
@pytest.mark.django_db
def test_password_change_requires_login(api_client, payload):
    payload = payload()
    response = api_client.patch(MYPAGEPASSWORDCHANGE_URL, data=payload, format="json")
    print(response.json())
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "로그인후 비밀번호를 변경 부탁드립니다."