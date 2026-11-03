from rest_framework_simplejwt.tokens import RefreshToken

from apps.devflow_ai.users.models.social_login_user import SocialUser


# 토큰 생성
def generate_jwt_tokens_for_user(user:SocialUser) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }
