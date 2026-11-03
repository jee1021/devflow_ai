import logging
from django.utils import timezone
from http import HTTPStatus

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from ninja import Router,Status
from ninja.errors import HttpError

from apps.devflow_ai.users.models import PhoneVerification
from apps.devflow_ai.users.schema.response import CommonSuccess, CommonError
from apps.devflow_ai.users.schema.schema import SignUp
from apps.devflow_ai.users.models.signup_user import SignupUser

logger = logging.getLogger(__name__)
router = Router(tags=["signup"])


@router.post(
    "",
    summary="회원가입",
    description="signup_post",
    response={
        HTTPStatus.CREATED: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.CONFLICT: CommonError,
        HTTPStatus.INTERNAL_SERVER_ERROR: CommonError,
    },
    auth=None,
)
def signup(request, payload: SignUp):

    if SignupUser.objects.filter(email=payload.email).exists():
        raise HttpError(HTTPStatus.BAD_REQUEST, "이미 가입된 이메일입니다.")

    if payload.username != payload.username_confirm:
        raise HttpError(HTTPStatus.BAD_REQUEST, "사용자 아이디가 일치 하지않습니다.")

    if SignupUser.objects.filter(username=payload.username).exists():
        raise HttpError(HTTPStatus.BAD_REQUEST, "이미 사용중인 아이디 입니다.")

    if SignupUser.objects.filter(phone_number=payload.phone_number).exists():
        raise HttpError(HTTPStatus.BAD_REQUEST, "이미 가입된 휴대폰입니다.")

    verification = PhoneVerification.objects.filter(
        code=payload.phone_verification_code,
        phone_number=payload.phone_number,
        expires_at__gte=timezone.now(),
        is_verified=True,
        is_used=False
    ).first()
    if not verification:
        raise HttpError(HTTPStatus.CONFLICT, "휴대폰 인증 센터에서 1차 검증후 가입서를 작성해주세요.")

    if not payload.agree_third_party:
        raise HttpError(HTTPStatus.CONFLICT, "제3자 정보제공 동의 체크후 가입서를 작성해주세요.")

    if payload.user_position is None:
        raise HttpError(HTTPStatus.BAD_REQUEST, "직군(user_position)을 선택해주세요.")
    if payload.user_profile is None:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "경력(user_profile)을 선택해주세요."
        )

    try:
        with transaction.atomic():
            user = SignupUser.objects.create(
                name=payload.name,
                email=payload.email,
                username=payload.username,
                username_confirm=payload.username_confirm,
                user_nickname=payload.user_nickname,
                password=payload.password,
                phone_number=payload.phone_number,
                birth_date=payload.birth_date,
                user_position=payload.user_position,
                user_profile=payload.user_profile,
                agree_third_party=payload.agree_third_party,
            )
            verification.is_used = True
            verification.save(update_fields=["is_used"])
    except ValueError as e:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(e))
    except (IntegrityError, ValidationError):
        raise HttpError(HTTPStatus.BAD_REQUEST, "이미 가입된 정보가 있습니다. 로그인해주세요")
    except Exception as e:
        logger.exception(f"회원가입 처리중 오류{str(e)}")
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, "회원가입 처리중 오류가 발생했습니다. 잠시후 다시 시도해주세요")

    return Status(HTTPStatus.CREATED, CommonSuccess(
        message="회원가입 성공!! 로그인 해주세요",
        data={
            "email": payload.email,
            "username": user.username,
            "user_nickname": user.user_nickname,
            "phone_number": user.phone_number,
            "user_profile": user.user_profile,
            "user_position": user.user_position,
        }
    ))


# =====================================================================
# 중복확인 라우터 (위 signup 코드는 수정하지 않고 아래에 추가)
#   GET /check-email?email=...
#   GET /check-username?username=...
#   GET /check-nickname?nickname=...
#   성공 응답: 200 {"message": "...", "data": {"available": true|false}}
# =====================================================================
@router.get(
    "/check-email",
    summary="이메일 중복확인",
    description="check_email_get",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
    },
    auth=None,
)
def check_email(request, email: str):
    email = email.strip()
    if not email:
        raise HttpError(HTTPStatus.BAD_REQUEST, "이메일을 입력해주세요.")

    available = not SignupUser.objects.filter(email=email).exists()
    return Status(HTTPStatus.OK, CommonSuccess(
        message="사용 가능한 이메일입니다." if available else "이미 가입된 이메일입니다.",
        data={"available": available},
    ))


@router.get(
    "/check-username",
    summary="아이디 중복확인",
    description="check_username_get",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
    },
    auth=None,
)
def check_username(request, username: str):
    username = username.strip()
    if not username:
        raise HttpError(HTTPStatus.BAD_REQUEST, "아이디를 입력해주세요.")

    available = not SignupUser.objects.filter(username=username).exists()
    return Status(HTTPStatus.OK, CommonSuccess(
        message="사용 가능한 아이디입니다." if available else "이미 사용중인 아이디입니다.",
        data={"available": available},
    ))


@router.get(
    "/check-nickname",
    summary="닉네임 중복확인",
    description="check_nickname_get",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
    },
    auth=None,
)
def check_nickname(request, nickname: str):
    nickname = nickname.strip()
    if not nickname:
        raise HttpError(HTTPStatus.BAD_REQUEST, "닉네임을 입력해주세요.")

    available = not SignupUser.objects.filter(user_nickname=nickname).exists()
    return Status(HTTPStatus.OK, CommonSuccess(
        message="사용 가능한 닉네임입니다." if available else "이미 사용중인 닉네임입니다.",
        data={"available": available},
    ))