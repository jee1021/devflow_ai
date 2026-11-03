import logging
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from ninja import Router
from ninja.errors import HttpError

from apps.devflow_ai.users.models.social_login_user import SocialUser
from apps.devflow_ai.users.schema.response import CommonError, CommonSuccess
from apps.devflow_ai.users.utills.kakao import (
format_full_birthday,
    generate_unique_nickname,
    get_kakao_access_token,
    get_kakao_user_info,
    normalize_phone_number,
)
from apps.devflow_ai.users.utils.generate_jwt_tokens_for_user import \
    generate_jwt_tokens_for_user


User = get_user_model()

router = Router(tags=["KakaoSocial"])
logger = logging.getLogger(__name__)


# ---- 내부 헬퍼 --------------------------------------------------------------


def _exchange_code_for_token(code: str) -> str:
    """인가 코드를 access_token으로 교환. 실패 시 적절한 HttpError를 발생시킨다."""
    access_token, error = get_kakao_access_token(code)

    if access_token:
        return access_token

    if "invalid_grant" in (error or ""):
        raise HttpError(HTTPStatus.BAD_REQUEST, "잘못된 인가 코드입니다.")

    raise HttpError(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        f"카카오 서버 오류: {error or '알 수 없는 오류'}",
    )


def _fetch_kakao_user_info(access_token: str) -> dict:
    user_info = get_kakao_user_info(access_token)

    if not user_info or not user_info.get("email") or not user_info.get("kakao_id"):
        raise HttpError(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "카카오 사용자 정보 요청 실패 또는 필수 정보 누락",
        )

    return user_info


def _get_or_create_user(user_info: dict) -> User:
    """
    카카오 provider_id 기준으로 기존 유저를 찾거나, 없으면 신규 생성한다.
    동시 요청에 의한 중복 생성은 select_for_update + IntegrityError 처리로 방어한다.
    """
    kakao_id = user_info["kakao_id"]

    try:
        with transaction.atomic():
            social_user = (
                SocialUser.objects.select_related("user")
                .select_for_update()
                .filter(provider="KAKAO", provider_id=kakao_id)
                .first()
            )
            if social_user:
                return social_user.user

            return _create_new_kakao_user(user_info)

    except IntegrityError:
        social_user = SocialUser.objects.select_related("user").get(
            provider="KAKAO", provider_id=kakao_id
        )
        return social_user.user


def _create_new_kakao_user(user_info: dict) -> User:
    kakao_id = user_info["kakao_id"]
    email = user_info["email"]
    name = user_info.get("name")
    gender = user_info.get("gender")

    raw_nickname = user_info.get("nickname") or f"kakao_{email.split('@')[0]}"
    nickname = generate_unique_nickname(raw_nickname)
    phone_number = normalize_phone_number(user_info.get("phone_number"))
    birthday = format_full_birthday(
        user_info.get("birthyear"), user_info.get("birthday")
    )

    # normalize_phone_number는 값이 없으면 "" 를 반환하므로 not phone_number로 함께 체크된다.
    required = {
        "name": name,
        "phone_number": phone_number,
        "birthday": birthday,
        "gender": gender,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        logger.warning("Kakao signup missing fields: %s", missing)
        raise HttpError(HTTPStatus.BAD_REQUEST, "잠시 후 다시 시도해주세요")

    user, _ = User.objects.get_or_create(
        email=email,
        defaults={
            "name": name,
            "nickname": nickname,
            "phone_number": phone_number,
            "birth_date": birthday,
            "gender": gender,
            "is_active": True,
        },
    )
    SocialUser.objects.create(user=user, provider="KAKAO", provider_id=kakao_id)
    return user


# ---- 엔드포인트 -------------------------------------------------------------




@router.get(
    "",
    summary="Kakao Social Login",
    description="카카오 소셜 로그인",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.INTERNAL_SERVER_ERROR: CommonError,
    },
)
def kakao_login(request, code: str):
    """카카오 OAuth 콜백 처리 (Django Ninja)."""

    access_token = _exchange_code_for_token(code)
    user_info = _fetch_kakao_user_info(access_token)
    user = _get_or_create_user(user_info)
    tokens = generate_jwt_tokens_for_user(user)

    return HTTPStatus.OK, CommonSuccess(**tokens, message="로그인 성공")