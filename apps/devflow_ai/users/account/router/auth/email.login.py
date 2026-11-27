import logging

from ninja import Router
from ninja.errors import HttpError
from http import HTTPStatus

from apps.devflow_ai.users.schema.auth.response import EmailSendOut

logger = logging.getLogger(__name__)
roter = Router(tags=['Email_login'])




@roter.post(
    "",
    summary="이메일로그인",
    description="이메일로그인",
    response={
        HTTPStatus.OK: EmailSendOut
    }
)
