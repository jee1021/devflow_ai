import logging
from http import HTTPStatus

from django.db import IntegrityError, transaction
from ninja import Router,Status
from ninja.errors import HttpError

from apps.devflow_ai.users.models.signup_user import SignupUser
from apps.devflow_ai.users.models.login_user_profile_mypage import LoginUserProfileMyPage
from apps.devflow_ai.users.schema.response import CommonSuccess, CommonError
from apps.devflow_ai.users.schema.schema import MypageUser

logger = logging.getLogger(__name__)
router = Router(tags=["mypage"])

USER_FIELDS = {"username", "user_nickname", "user_profile", "user_position"}
PROFILE_FIELDS = {"phone_number", "user_profile", "user_position", "username", "user_nickname"}





@router.patch(
    "",
    summary="마이페이지",
    description="my_page",
    auth=None,
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.NOT_FOUND: CommonError,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.UNAUTHORIZED: CommonError,
        HTTPStatus.CONFLICT: CommonError,
    }
)
def mypage(request,payload:MypageUser):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        raise HttpError(HTTPStatus.UNAUTHORIZED, "로그인이 필요합니다.")
    try:
        user = SignupUser.objects.get(username=request.user.username)
        if payload.username is not None and payload.username != payload.username_confirm:
            raise HttpError(HTTPStatus.BAD_REQUEST, "사용자 아이디가 일치 하지않습니다.")
        if payload.password is not None and payload.password != payload.password_confirm:
            raise HttpError(HTTPStatus.BAD_REQUEST, "비밀번호가 일치 하지않습니다.")
        profile, _ = LoginUserProfileMyPage.objects.get_or_create(user=user)

        payload_data = payload.dict(exclude_unset=True)
        user_fields = {k: v for k, v in payload_data.items() if k in USER_FIELDS}
        profile_payload = payload

        with transaction.atomic():
            for attr, value in user_fields.items():
                setattr(user, attr, value)
            update_fields = list(user_fields.keys())
            if payload.password is not None:
                user.set_password(payload.password)
                update_fields.append("password")
            if update_fields:
                user.save(update_fields=update_fields)

            # LoginUserProfileMyPage 업데이트
            profile_fields = {
                k: v for k, v in profile_payload.dict(exclude_unset=True).items()
                if k in PROFILE_FIELDS
            }
            for attr, value in profile_fields.items():
                setattr(profile, attr, value)
            if profile_fields:
                profile.save(update_fields=profile_fields.keys())

    except HttpError:
        raise
    except SignupUser.DoesNotExist:
        raise HttpError(HTTPStatus.NOT_FOUND, "유저를 찾을 수 없습니다.")
    except IntegrityError:
        raise HttpError(HTTPStatus.CONFLICT, "이미 사용 중인 정보가 있습니다.")
    except Exception as e:
        logger.error(f"마이페이지 정보 수정을 실패했습니다. {e}")
        raise HttpError(HTTPStatus.BAD_REQUEST, "수정에 실패했습니다.")

    return Status(HTTPStatus.OK, CommonSuccess(message="마이페이지 정보 수정을 성공했습니다."))