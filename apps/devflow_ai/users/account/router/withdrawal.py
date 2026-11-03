import logging
from sqlite3 import DatabaseError
from ninja import Router
from http import HTTPStatus
from ninja.errors import HttpError
from apps.devflow_ai.users.schema.response import WithdrawalSuccess, WithdrawalError
from apps.devflow_ai.users.models import Withdrawal


router = Router(tags=["withdrawal"])
logger=logging.getLogger(__name__)

@router.delete(
    "",
    summary="withdrawal",
    description="회원탈퇴",
    auth=None,
    response={
        HTTPStatus.OK: WithdrawalSuccess,
        HTTPStatus.BAD_REQUEST: WithdrawalError,
        HTTPStatus.NOT_FOUND: WithdrawalError,
    }
)
def withdrawal(request):

    try :
        Withdrawal.obj = Withdrawal.objects.filter(user=request.user)
    except Withdrawal.DoesNotExist :
        logger.warning(f"탈퇴신청 내역이 없음:user={request.user.pk}")
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "탈퇴 신청내역이 없습니다."
        )
    try :
        Withdrawal.delete()
    except DatabaseError :
        logger.exception(f"탈퇴처리중 오류:user={request.user.pk}")
        raise HttpError(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "탈퇴 처리중 오류가 밣생했습니다."
        )
    Withdrawal.objects.create(
        user=request.user,
        reason=Withdrawal.reason,
        status=Withdrawal.status,
        reason_detail=Withdrawal.reason_detail,
    )
    return HTTPStatus.OK,WithdrawalSuccess(
        message= "탈퇴 신청이 완료 되었습니다."
    )



