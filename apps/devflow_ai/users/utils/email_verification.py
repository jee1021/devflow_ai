

import hashlib
import hmac
import secrets

from django.conf import settings
from django_redis import get_redis_connection

KEY_PREFIX = "email_verification"

CODE_LENGTH = 6
CODE_TTL = 300
VERIFIED_TTL = 1800
MAX_ATTEMPTS = 3
RESEND_COOLDOWN = 60
MAX_SENDS_PER_HOUR = 6
SENDS_WINDOW = 3600


ALLOWED_PURPOSES = {"signup", "reset"}


class EmailVerificationError(Exception):
    """이메일 인증 관련 예외의 공통 부모."""


class VerificationRateLimited(EmailVerificationError):
    """재발송이 너무 빠르거나 시간당 발송 한도를 넘었을 때 발생."""


def _r():
    return get_redis_connection("default")


def _key(kind: str, purpose: str, email: str) -> str:
    if purpose not in ALLOWED_PURPOSES:
        raise ValueError(f"Unknown purpose: {purpose!r}")
    return f"{KEY_PREFIX}:{kind}:{purpose}:{email.strip().lower()}"


def generate_code() -> str:

    return f"{secrets.randbelow(10 ** CODE_LENGTH):0{CODE_LENGTH}d}"


def _digest(purpose: str, email: str, code: str) -> bytes:

    msg = f"{purpose}:{email.strip().lower()}:{code}".encode("utf-8")
    key = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest().encode("ascii")


def issue_code(purpose: str, email: str) -> str:

    r = _r()

    if not r.set(_key("cooldown", purpose, email), "1", nx=True, ex=RESEND_COOLDOWN):
        raise VerificationRateLimited("잠시 후 다시 시도해 주세요.")

    sends_key = _key("sends", purpose, email)
    sends = r.incr(sends_key)
    if sends == 1:
        r.expire(sends_key, SENDS_WINDOW)
    if sends > MAX_SENDS_PER_HOUR:
        raise VerificationRateLimited("인증 요청 횟수를 초과했어요. 나중에 다시 시도해 주세요.")

    code = generate_code()
    r.set(_key("code", purpose, email), _digest(purpose, email, code), ex=CODE_TTL)
    return code


def code_ttl_remaining(purpose: str, email: str) -> int:
    ttl = _r().ttl(_key("code", purpose, email))
    return max(ttl, 0)  # -2(키 없음), -1(만료 없음)은 0으로 처리


def verify_code(purpose: str, email: str, input_code: str) -> bool:

    r = _r()
    code_key = _key("code", purpose, email)
    attempts_key = _key("attempts", purpose, email)

    # 먼저 횟수를 올린 뒤 검사한다. (동시 요청으로 제한을 우회하는 것 방지)
    attempts = r.incr(attempts_key)
    if attempts == 1:
        r.expire(attempts_key, CODE_TTL)
    if attempts > MAX_ATTEMPTS:
        r.delete(code_key)  # 한도 초과 시 코드 폐기: 새 코드를 받아야만 재시도 가능
        return False

    saved = r.get(code_key)
    if not saved:
        return False

    candidate = _digest(purpose, email, (input_code or "").strip())
    if not hmac.compare_digest(saved, candidate):
        return False

    if r.delete(code_key) != 1:
        return False

    r.delete(attempts_key)
    r.set(_key("verified", purpose, email), "1", ex=VERIFIED_TTL)
    return True


def is_verified(purpose: str, email: str) -> bool:
    return _r().exists(_key("verified", purpose, email)) == 1


def consume_verified(purpose: str, email: str) -> bool:

    return _r().delete(_key("verified", purpose, email)) == 1