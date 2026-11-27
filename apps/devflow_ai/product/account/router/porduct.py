from datetime import datetime
from typing import List, Optional

from django.db import models
from ninja import Router, Schema
from ninja.security import django_auth  # JWT 등을 쓰면 해당 인증 클래스로 교체

from apps.devflow_ai.product.models import Product
from apps.devflow_ai.product.models.product import is_trainee, PointRedemption, UserPass, \
    AttendancePoint, RedeemError
from apps.devflow_ai.product.schema.schema import ProductOut, FeatureStatusOut, ErrorOut, \
    PointBalanceOut, PointHistoryOut, RedeemIn, RedeemOut, RedemptionOut, UserPassOut

router = Router(tags=["passes"], auth=django_auth)



@router.get("/products", response=List[ProductOut])
def list_products(request, points_only: bool = False):
    """상품 목록. 예비개발자 전용 상품은 예비개발자에게만 노출."""
    user = request.user
    qs = Product.objects.all().order_by("id")

    if not is_trainee(user):
        qs = qs.filter(is_trainee_only=False)
    if points_only:
        qs = qs.filter(required_points__gt=0)

    redeemed_ids = set(
        PointRedemption.objects.filter(user=user).values_list("product_id", flat=True)
    )
    return [
        ProductOut(
            id=p.id,
            name=p.name,
            price=p.price,
            period_months=p.period_months,
            plan_type=p.plan_type,
            required_points=p.required_points,
            is_trainee_only=p.is_trainee_only,
            redeemed=p.id in redeemed_ids,
        )
        for p in qs
    ]


# ---------- 이용권 ----------

@router.get("/passes/me", response=List[UserPassOut])
def my_passes(request):
    """내 이용권 목록 (기능별 1건)."""
    return UserPass.objects.filter(user=request.user).order_by("feature")


@router.get("/passes/me/{feature}", response={200: FeatureStatusOut, 404: ErrorOut})
def my_pass_status(request, feature: str):
    """특정 기능의 이용권이 현재 유효한지 확인."""
    if feature not in UserPass.Feature.values:
        return 404, {"detail": "존재하지 않는 기능입니다."}
    return {
        "feature": feature,
        "active": UserPass.has_active(request.user, feature),
    }


# ---------- 출석 포인트 ----------

@router.get("/points/me", response=PointBalanceOut)
def my_point_balance(request):
    return {"balance": AttendancePoint.balance(request.user)}


@router.get("/points/me/history", response=List[PointHistoryOut])
def my_point_history(request, limit: int = 50, offset: int = 0):
    limit = max(1, min(limit, 200))
    return AttendancePoint.objects.filter(user=request.user).order_by(
        "-created_at", "-id"
    )[offset : offset + limit]


# ---------- 포인트 교환 ----------

@router.post(
    "/redemptions",
    response={201: RedeemOut, 400: ErrorOut, 404: ErrorOut},
)
def redeem_product(request, payload: RedeemIn):
    """출석 포인트로 상품 교환 → 이용권 지급/연장."""
    product = Product.objects.filter(pk=payload.product_id).first()
    if product is None:
        return 404, {"detail": "상품을 찾을 수 없습니다."}

    try:
        UserPass.redeem_with_points(request.user, product)
    except RedeemError as e:
        return 400, {"detail": str(e)}

    return 201, {
        "product_id": product.id,
        "points_used": product.required_points,
        "balance": AttendancePoint.balance(request.user),
        "passes": list(UserPass.objects.filter(user=request.user).order_by("feature")),
    }


@router.get("/redemptions/me", response=List[RedemptionOut])
def my_redemptions(request):
    return PointRedemption.objects.filter(user=request.user).order_by("-created_at")


