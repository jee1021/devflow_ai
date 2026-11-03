from ninja import Router

from .signup import router as signup_router
from .login import router as login_router
from .kakao_social import router as kakao_social_router
from .withdrawal import router as withdrawal_router
from .mypage import router as mypage_router
from .mypagenotificationcenter import router as mypage_notification_center_router
from .mypage_notification_center_list import router as mypage_notification_center_list_router
from .mypage_passwordchange import router as mypage_password_change_router

__all__=["router"]


router = Router()
#signup & login
router.add_router("/signup",signup_router),
router.add_router("/login",login_router),

#mypage
router.add_router("/mypage",mypage_router),
router.add_router("/mypage_notification_center",mypage_notification_center_router),
router.add_router("/mypage_notification_center_list", mypage_notification_center_list_router),
router.add_router("/mypage_password_change", mypage_password_change_router),

#social
router.add_router("/kakao-social",kakao_social_router),

#withdrawal
router.add_router("/withdrawal",withdrawal_router),


