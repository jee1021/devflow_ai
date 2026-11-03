import logging
from http import HTTPStatus

from django.contrib.auth import login as auth_login
from django.db import transaction
from ninja import Router,Status
from ninja.errors import HttpError

from apps.devflow_ai.users.models.signup_user import SignupUser
from apps.devflow_ai.users.schema.response import CommonSuccess, CommonError
from apps.devflow_ai.users.schema.schema import Login

logger = logging.getLogger(__name__)
router = Router(tags=["login"])

@router.post(
    "",
    summary="로그인",
    description="login.post",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.NOT_FOUND: CommonError,
        HTTPStatus.INTERNAL_SERVER_ERROR: CommonError,
    },
    auth=None
)
def login(request,payload: Login):
    if not payload.username or not payload.username.strip():
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "아이디를 입력해주세요."
        )
    if not payload.password or not payload.password.strip():
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "비밀번호를 입력해주세요."
        )
    if not payload.user_nickname or not payload.user_nickname.strip():
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "닉네임을 입력해주세요."
        )
    if not payload.user_position :
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "직군(user_position)을 선택해주세요."
        )
    if not payload.user_profile:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "경력(user_profile)을 선택해주세요."
        )
    try:
        user = SignupUser.objects.get(username=payload.username)
        if user.user_position != payload.user_position:
            raise HttpError(
                HTTPStatus.NOT_FOUND,
                "직군정보가 일치하지 않습니다."
            )
        if user.user_nickname != payload.user_nickname:
            raise HttpError(
                HTTPStatus.NOT_FOUND,
                "닉네임이 일치하지 않습니다."
            )
        with transaction.atomic():
            if not user.check_password(payload.password):
                raise HttpError(
                    HTTPStatus.NOT_FOUND,
                    "비밀번호가 일치하지 않습니다."
                )
        auth_login(request, user)
    except SignupUser.DoesNotExist:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "아이디가 일치하지 않습니다."
        )
    except HttpError:
        raise
    except Exception as e:
        logger.exception(f"로그인 시도중 시스템에러{str(e)}")
        raise HttpError(
            HTTPStatus.INTERNAL_SERVER_ERROR,

            "로그인 시도중 시스템 에러가 발생했습니다."
        )
    return Status(HTTPStatus.OK,CommonSuccess(
        message="devflow_ai 로그인 성공!!",
        data={
            "username": user.username,
             "user_nickname": user.user_nickname,
            "user_profile": user.user_profile,
            "user_position": user.user_position,
        }
    ))