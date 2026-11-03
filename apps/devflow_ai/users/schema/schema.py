from datetime import date
from typing import Literal
from ninja import Schema
from pydantic import EmailStr, Field
from pydantic import field_validator



class SignUp(Schema):
    name: str = Field(...,max_length=25,description="이름",)
    email: EmailStr
    username: str = Field(...,min_length=7,max_length=13,
    pattern=r"^[\w!@#$%^&*()\-+=]{7,13}$",
    description="사용자 아이디",
    )
    username_confirm: str = Field(...,min_length=7,max_length=13,
        pattern=r"^[\w!@#$%^&*()\-+=]{7,13}$",
        description="사용자 아이디 확인",
    )
    user_nickname: str = Field(
        ...,
        min_length=2,
        max_length=13,
        description="사용자 닉네임",
    )
    password: str = Field(...,min_length=7,max_length=20,description="비밀번호",)
    password_confirm: str = Field(...,min_length=7,max_length=20,description="비밀번호 확인",)
    birth_date: date
    phone_number: str = Field(
        ...,
        max_length=20,
        description="휴대폰 번호",
    )
    user_profile: Literal["JUNIOR","MIDDLE","SENIOR",
    ] | None = None
    user_position: Literal["BACKEND_ENGINEER","FRONT_ENGINEER","FULLSATCK_ENGINEER",
        "UXUI_DESIGNER","BUSINESS_ANALYST","PROJECT_MANAGER",
        "CEO",
        "ASPIRING_JUNIOR",
    ] | None = None
    @field_validator("user_position", "user_profile", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    phone_verification_code: str

    agree_third_party: bool




class KakaoSocial_LogIn(Schema):
    code: str

class WithdrawalCancel(Schema):
    reason: Literal["ETC","NOT_SATISFIED"] | None = None
    status: Literal["PENDING","COMPLETED","CANCELED"] | None = None
    reason_detail: str = Field()


class WithdrawalAccount(Schema):
    reason: Literal["ETC", "NOT_SATISFIED"] | None = None
    reason_detail: str | None = None
    status: Literal["PENDING", "COMPLETED", "CANCELED"] | None = None



class Login(Schema):
    username: str | None = None
    user_nickname: str | None = None
    password: str | None = None
    user_profile: Literal["JUNIOR", "MIDDLE", "SENIOR"] | None = None
    user_position: Literal[
        "BACKEND_ENGINEER", "FRONTEND_ENGINEER", "FULLSTACK_ENGINEER",
        "UXUI_DESIGNER", "BUSINESS_ANALYST", "PROJECT_MANAGER",
        "CEO", "OTHER"
    ] | None = None


class MypageUser(Schema):
    user_profile: Literal["JUNIOR", "MIDDLE", "SENIOR"] | None = None
    user_position: Literal[
                       "BACKEND_ENGINEER", "FRONTEND_ENGINEER", "FULLSTACK_ENGINEER",
                       "UXUI_DESIGNER", "BUSINESS_ANALYST", "PROJECT_MANAGER",
                       "CEO", "OTHER"
                   ] | None = None
    phone_number: str = Field(
        ...,
        max_length=20,
        description="휴대폰 번호",
    )
    username: str = Field(...,min_length=7,max_length=13,
                          pattern=r"^[\w!@#$%^&*()\-+=]{7,13}$",
                          description="사용자 아이디",
                          )
    username_confirm: str = Field(...,min_length=7,max_length=13,
                                  pattern=r"^[\w!@#$%^&*()\-+=]{7,13}$",
                                  description="사용자 아이디 확인",
                                  )
    user_nickname: str = Field(
        ...,
        min_length=2,
        max_length=13,
        description="사용자 닉네임",
    )
    password: str = Field(...,min_length=7,max_length=20,description="비밀번호",)
    password_confirm: str = Field(...,min_length=7,max_length=20,description="비밀번호 확인",)

class MyPageNotificationCenter(Schema):
    code: bool = None
    pr_review: bool = None
    code_refactoring: bool = None
    meeting_notice: bool = None
    maintenance: bool = None
    pr_approved : bool = None
    pr_rejected: bool = None


class MyPageNotificationCenterList(Schema):
    code: bool = None
    pr_review: bool = None
    code_refactoring: bool = None
    meeting_notice: bool = None
    maintenance: bool = None
    pr_approved: bool = None
    pr_rejected: bool = None
    mention: bool = None
    MyPageNotification: Literal[
        "PR_REVIEW",
        "CODE_REFACTORING",
        "MEETING_NOTICE",
        "MAINTENANCE",
        "PR_APPROVED",
        "PR_REJECTED",
        "MENTION",
    ] | None = None
    MyPageNotification_Status: Literal[
        "PENDING", "NONE", "APPROVED", "REJECTED"
    ] | None = None



class MyPagePasswordChange(Schema):
    current_password: str
    new_change_password: str
    new_change_password_confirm: str



class CartAddIn(Schema):
    product_id: int
    quantity: int = Field(1, ge=1)

class CartQuantityIn(Schema):
    quantity: int = Field(..., ge=1)

class CartItemIdsIn(Schema):
    item_ids: list[int] = Field(..., min_length=1)



class CheckoutIn(Schema):
    item_ids: list[int] | None = None  # None 이면 장바구니 전체 결제


class CartItemOut(Schema):
    id: int
    product_id: int
    quantity: int
    unit_price: int
    discounted_unit_price: int
    original_total: int
    discounted_total: int


class MyPageCartOut(Schema):
    mypage_cart_type: Literal["NORMAL", "VIP_NORMAL"]
    purchase_count: int
    discount_rate: int
    max_items: int | None
    items: list[CartItemOut]
    total_original_price: int
    total_discounted_price: int


class CheckoutOut(Schema):
    order_id: int
    purchase_count: int
    mypage_cart_type: Literal["NORMAL", "VIP_NORMAL"]

