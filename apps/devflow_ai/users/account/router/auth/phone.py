import hmac
import logging
import re
import secrets
from datetime import timedelta
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from ninja import Router, Status
from ninja.errors import HttpError

from apps.devflow_ai.users.models.auth.phone_verification import PhoneVerification
from apps.devflow_ai.users.schema.auth.schema import PhoneSendIn, VerifyIn
from apps.devflow_ai.users.schema.response import CommonError, CommonSuccess

logger = logging.getLogger(__name__)
router = Router(tags=["phone"])

OTP_LENGTH = 6
OTP_TTL = timedelta(minutes=5)
MAX_ATTEMPTS = 5
MAX_RAW_PHONE_LEN = 30
PHONE_PATTERN = re.compile(r"01[016789]\d{7,8}$")


def _cfg(name, default):
    return getattr(settings, name, default)


def normalize_phone(raw: str) -> str:
    if len(raw or "") > MAX_RAW_PHONE_LEN:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "올바른 전화번호가 아닙니다.",
        )
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("82"):
        rest = digits[2:]
        if rest.startswith("0"):
            rest = rest[1:]
        digits = "0" + rest
    if not PHONE_PATTERN.fullmatch(digits):
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "올바른 전화번호가 아닙니다.",
        )
    return digits


def client_ip(request) -> str | None:
    meta = request.META
    if _cfg("PHONE_AUTH_TRUST_PROXY", False):
        xff = meta.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
    return meta.get("REMOTE_ADDR")


def _incr(key: str, ttl: int) -> int:
    cache.add(key, 0, ttl)
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 1, ttl)
        return 1


def send_sms(phone: str, code: str) -> None:
    if _cfg("PHONE_AUTH_SENDER", "console") == "real":
        raise HttpError(
            HTTPStatus.SERVICE_UNAVAILABLE,
            "문자 발송이 준비되지 않았습니다. 잠시 후 다시 시도해주세요.",
        )
    logger.info("[DEV SMS] to=%s", phone)
    logger.debug("[DEV SMS] code=%s", code)


@router.post(
    "/send",
    summary="휴대폰 인증번호 발송",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.TOO_MANY_REQUESTS: CommonError,
        HTTPStatus.SERVICE_UNAVAILABLE: CommonError,
    },
    auth=None,
)
def send_code(request, payload: PhoneSendIn):
    phone = (payload.phone or "").strip()
    normalize_phone(phone)
    now = timezone.now()
    qs = PhoneVerification.objects.filter(phone_number=phone)

    cooldown = _cfg("PHONE_AUTH_RESEND_COOLDOWN", 60)
    last = qs.order_by("-created_at").first()
    if last and (now - last.created_at).total_seconds() < cooldown:
        raise HttpError(
            HTTPStatus.TOO_MANY_REQUESTS,
            f"{cooldown}초 후에 다시 요청해주세요.",
        )
    if qs.filter(created_at__gte=now - timedelta(hours=1)).count() >= _cfg(
        "PHONE_AUTH_MAX_SENDS_PER_HOUR", 5
    ):
        raise HttpError(
            HTTPStatus.TOO_MANY_REQUESTS,
            "인증 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
        )

    ip = client_ip(request)
    if ip and _incr(f"phoneauth:ip:{ip}", 3600) > _cfg(
        "PHONE_AUTH_MAX_SENDS_PER_IP_HOUR", 20
    ):
        raise HttpError(
            HTTPStatus.TOO_MANY_REQUESTS,
            "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
        )

    code = "".join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))
    qs.filter(is_verified=False, expires_at__gt=now).update(expires_at=now)
    PhoneVerification.objects.create(
        phone_number=phone,
        code=code,
        expires_at=now + OTP_TTL,
    )
    send_sms(phone, code)

    data = {"expires_in": int(OTP_TTL.total_seconds())}
    if settings.DEBUG:
        data["debug_code"] = code
    return Status(
        HTTPStatus.OK,
        CommonSuccess(message="인증번호를 발송했습니다.", data=data),
    )


@router.post(
    "/verify",
    summary="휴대폰 인증번호 확인",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.BAD_REQUEST: CommonError,
        HTTPStatus.TOO_MANY_REQUESTS: CommonError,
    },
    auth=None,
)
def verify_code(request, payload: VerifyIn):
    phone = (payload.phone or "").strip()
    normalize_phone(phone)
    now = timezone.now()
    input_code = (payload.code or "").strip()
    if not re.fullmatch(rf"\d{{{OTP_LENGTH}}}", input_code):
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "인증번호 형식이 올바르지 않습니다.",
        )

    rec = (
        PhoneVerification.objects.filter(
            phone_number=phone,
            is_verified=False,
            expires_at__gt=now,
        )
        .order_by("-created_at")
        .first()
    )
    if not rec:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "인증번호가 만료되었거나 요청 내역이 없습니다.",
        )

    attempts = _incr(
        f"phoneauth:attempts:{rec.pk}",
        int(OTP_TTL.total_seconds()) + 60,
    )
    if attempts > MAX_ATTEMPTS:
        PhoneVerification.objects.filter(pk=rec.pk).update(expires_at=now)
        raise HttpError(
            HTTPStatus.TOO_MANY_REQUESTS,
            "시도 횟수를 초과했습니다. 인증번호를 다시 요청해주세요.",
        )

    stored = (rec.code or "").strip()
    if len(stored) != OTP_LENGTH or not hmac.compare_digest(stored, input_code):
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "인증번호가 일치하지 않습니다.",
        )

    updated = PhoneVerification.objects.filter(
        pk=rec.pk,
        is_verified=False,
        expires_at__gt=now,
    ).update(is_verified=True, verified_at=now)
    if updated != 1:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "이미 처리되었거나 만료된 인증입니다.",
        )

    return Status(
        HTTPStatus.OK,
        CommonSuccess(
            message="휴대폰 인증이 완료되었습니다.",
            data={"phone_number": phone},
        ),
    )
