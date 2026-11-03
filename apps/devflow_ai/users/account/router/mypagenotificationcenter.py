import logging

from ninja.errors import HttpError
from ninja import Router,Status
from http import HTTPStatus
from django.forms.models import model_to_dict

from apps.devflow_ai.users.schema.response import CommonSuccess, CommonError
from apps.devflow_ai.users.models.mypage_notificationCenter_user import MyPageNotificationCenterUser

logger = logging.getLogger(__name__)
router = Router(tags=["mypagenotificationcenter"])

@router.get(
    "",
    summary="마이페이지-알림센터",
    auth=None,
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.NOT_FOUND: CommonError,
        HTTPStatus.INTERNAL_SERVER_ERROR: CommonError,
        HTTPStatus.UNAUTHORIZED:CommonError

    }
)
def mypage_notificationcenter(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        raise HttpError(
            HTTPStatus.UNAUTHORIZED,
            "로그인이 필요합니다."
        )
    try:
        center = MyPageNotificationCenterUser.objects.get(user=request.user)
    except MyPageNotificationCenterUser.DoesNotExist:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "알림이 존재하지 않습니다."
        )
    except Exception as e :
        logger.exception(f"마이페이지 알림센터 알림조회 실패{str(e)}")
        raise HttpError(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "마이페이지 알림센터 조회에 실패 했습니다."
        )
    return Status(HTTPStatus.OK, CommonSuccess(
        message="조회에 성공!!",
        data={"center": model_to_dict(center)},
    ))





