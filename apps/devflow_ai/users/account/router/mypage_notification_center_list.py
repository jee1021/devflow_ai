import logging
from http import HTTPStatus

from django.db import IntegrityError
from ninja import Router
from ninja.errors import HttpError

from apps.devflow_ai.users.models.mypage_notificationCenter_user import MyPageNotificationCenterUser
from apps.devflow_ai.users.models.mypage_notificationcenter_list import MyPageNotificationCenterList
from apps.devflow_ai.users.models.notificationtype import NotificationType
from apps.devflow_ai.users.schema.response import CommonError, CommonSuccess
from apps.devflow_ai.users.schema.schema import MyPageNotificationCenterList

logger = logging.getLogger(__name__)
router = Router(tags=["mypage_notification_center_list"])

NOTIFICATION_TYPE_CODES = {
    "PR_REVIEW": "pr_review",
    "CODE_REFACTORING": "code_refactoring",
    "MEETING_NOTICE": "meeting_notice",
    "MAINTENANCE": "maintenance",
    "PR_APPROVED": "pr_approved",
    "PR_REJECTED": "pr_rejected",
    "MENTION": "mention",
}


@router.post(
    "",
    summary="마이페이지 알림센터 리스트 신청",
    description="mypage_notification_center_list",
    auth=None,
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.NOT_FOUND: CommonError,
        HTTPStatus.UNAUTHORIZED: CommonError,
        HTTPStatus.CONFLICT: CommonError,
    },
)
def mypage_notification_center_list(request, payload: MyPageNotificationCenterList):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        raise HttpError(HTTPStatus.UNAUTHORIZED, "로그인이 필요합니다.")
    if payload.MyPageNotification is None:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "마이페이지(MyPageNotification)알림신청을 선택해주세요",
        )
    if payload.MyPageNotification_Status is None:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "마이페이지(MyPageNotification_Status)를 알림신청상태를 선택해주세요",
        )

    try:
        center = MyPageNotificationCenterUser.objects.get(user=request.user)
        notification_code = NOTIFICATION_TYPE_CODES[payload.MyPageNotification]
        notification_label = MyPageNotificationCenterList.MyPageNotification(
            payload.MyPageNotification
        ).label
        notification_type, _ = NotificationType.objects.get_or_create(
            code=notification_code,
            defaults={"label": notification_label},
        )
        item = MyPageNotificationCenterList.objects.create(
            center=center,
            mypage_notification=payload.MyPageNotification,
            mypage_notification_Status=payload.MyPageNotification_Status,
            notification_type=notification_type,
            title=notification_label,
        )
        return HTTPStatus.OK, CommonSuccess(
            message="마이페이지 알림센터 신청에 성공했습니다.",
            data={"id": item.id},
        )
    except HttpError:
        raise
    except MyPageNotificationCenterUser.DoesNotExist:
        raise HttpError(HTTPStatus.NOT_FOUND, "알림센터를 찾지못했습니다.")
    except IntegrityError:
        raise HttpError(HTTPStatus.CONFLICT, "이미 신청된 알림이 있습니다.")
    except Exception as e:
        logger.error("마이페이지 알림센터 신청에 실패했습니다. %s", e)
        raise HttpError(HTTPStatus.BAD_REQUEST, "마이페이지 알림센터 신청에 실패했습니다.")
