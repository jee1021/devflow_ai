from datetime import datetime
from typing import List

from ninja import Schema


class ErrorOut(Schema):
    detail: str


class ProductOut(Schema):
    id: int
    name: str
    price: int
    period_months: int
    plan_type: str
    required_points: int
    is_trainee_only: bool
    redeemed: bool = False  # 이미 포인트로 교환했는지


class UserPassOut(Schema):
    feature: str
    expires_at: datetime
    is_active: bool


class PointBalanceOut(Schema):
    balance: int


class PointHistoryOut(Schema):
    id: int
    points: int
    reason: str
    created_at: datetime


class RedeemIn(Schema):
    product_id: int


class RedeemOut(Schema):
    product_id: int
    points_used: int
    balance: int
    passes: List[UserPassOut]


class RedemptionOut(Schema):
    id: int
    product_id: int
    points_used: int
    created_at: datetime


class FeatureStatusOut(Schema):
    feature: str
    active: bool


# ---------- 상품 ----------