from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.security import django_auth
from apps.devflow_ai.users.account.router import router as account_router
from apps.devflow_ai.users.schema.response import CommonError
from ninja.errors import ValidationError
from django.http import JsonResponse
api = NinjaAPI(
    title="DevFlow AI",
    version="1.0.0",
    urls_namespace="api",
    auth=django_auth
)
api.add_router("/users", account_router)


@api.exception_handler(HttpError)
def custom_error_handler(request, exc: HttpError):
    return api.create_response(
        request,
        CommonError(success=False, message=exc.message),
        status=exc.status_code,
    )



@api.exception_handler(ValidationError)
def custom_validation_errors(request, exc):
    first_error = exc.errors[0]
    field = first_error["loc"][-1]
    field_messages = {
        "user_position": "직군(user_position)을 선택해주세요.",
        "user_profile":  "경력(user_profile)을 선택해주세요.",
        "MyPageNotification_Status": "마이페이지(MyPageNotification_Status)를 알림신청상태를 선택해주세요",
        "MyPageNotification": "마이페이지(MyPageNotification)알림신청을 선택해주세요",
    }
    message = field_messages.get(field, "잘못된 요청입니다.")
    return JsonResponse(
        {"success": False, "message": message},
        status=400,
    )