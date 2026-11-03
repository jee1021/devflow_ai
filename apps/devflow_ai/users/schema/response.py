from ninja import Schema
from typing import Optional,Dict



class CommonSuccess(Schema):
    success: bool = True
    message: str
    data: dict | None = None



class CommonError(Schema):
    success: bool = False
    message: str


class TokenResponse(Schema):
    access_token: str
    refresh_token: str
    # 실제 generate_jwt_tokens_for_user 반환 형태에 맞게 필드 조정해주세요.


class ErrorResponse(Schema):
    detail: str


class WithdrawalError(Schema):
    success: bool = False
    message: str
    data: Optional[Dict] = None

class WithdrawalSuccess(Schema):
    success: bool = True
    message: str
    data: Optional[Dict] = None


class WithdrawalAccountError(Schema):
    success: bool = False
    message: str
    data: Optional[Dict] = None

class WithdrawalAccountSuccess(Schema):
    success: bool = True
    message: str
    data: Optional[Dict] = None

