import logging
from http import HTTPStatus

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from ninja import Router,Status
from ninja.errors import HttpError, ValidationError

from apps.devflow_ai.users.schema.response import CommonError, CommonSuccess
from apps.devflow_ai.users.schema.schema import MyPagePasswordChange

router = Router(tags=["MyPagePasswordChange"])
logger = logging.getLogger(__name__)

@router.patch(
    "",
    summary="비밀번호 변경",
    description="비밀번호 변경",
    auth=None,
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.UNAUTHORIZED: CommonError,
    }
)
def mypage_password_change(request,payload:MyPagePasswordChange):
    user = request.user
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        raise HttpError(HTTPStatus.UNAUTHORIZED,  "로그인후 비밀번호를 변경 부탁드립니다.")
    if not user.check_password(payload.current_password):
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "현재 비밀번호가 올바르지 않습니다."
        )
    if payload.new_change_password != payload.new_change_password_confirm:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "새비밀번호가 일치하지 않습니다."
        )
    try:
        validate_password(payload.new_change_password, user)
    except ValidationError as e:
        logger.warning(f"비밀번호 변경실패{str(e)}")
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "비밀번호 변경에 실패했습니다.".join(e.messages),
        )
    user.check_password(payload.new_change_password)
    user.save()
    update_session_auth_hash(request, user)
    return Status(HTTPStatus.OK, CommonSuccess(
        message="비밀번호 변경성공",
        data={
            payload.current_password:"current_password",
            payload.new_change_password: "payload.new_change_password",
        }
    ))
