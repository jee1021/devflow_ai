import logging

from django.core.exceptions import ValidationError
from ninja import Router, Status
from ninja.errors import HttpError
from http import HTTPStatus


from apps.devflow_ai.users.models.mypage_cart import MyPageCart
from apps.devflow_ai.users.schema.response import CommonError, CommonSuccess
from apps.devflow_ai.users.schema.schema import MyPageCartOut, CartAddIn

logger = logging.getLogger(__name__)
router = Router(tags=["mypage_cart"])


def _get_cart(request) -> MyPageCart:
    cart, _ = MyPageCart.objects.get_or_create(user=request.user)
    return cart


@router.get(
    "",
    summary="장바구니 조회",
    description="장바구니 상품조회",
    response={
        HTTPStatus.OK: MyPageCartOut,
    }
)
def get_cart(request):
    cart = _get_cart(request)
    # 쿼리 1번으로 가져오고 합계도 이 리스트로 계산 (프로퍼티 사용 시 쿼리 중복)
    items = list(cart.items.select_related("product", "cart").order_by("-created_at"))

    return HTTPStatus.OK, {
        "mypage_cart_type": cart.mypage_cart_type,
        "purchase_count": cart.purchase_count,
        "discount_rate": cart.discount_rate,
        "max_items": cart.max_items,
        "items": items,
        "total_original_price": sum(it.original_total for it in items),
        "total_discounted_price": sum(it.discounted_total for it in items),
    }


#장바구니 상품 담기
@router.post(
    "",
    summary="장바구니 상품담기",
    description="장바구니 상품 담기",
    response={
        HTTPStatus.OK: CommonSuccess,
        HTTPStatus.NOT_FOUND: CommonError,
        HTTPStatus.NOT_ACCEPTABLE: CommonError,

    }

)
def add_cart_item(request,payload: CartAddIn):
    cart = _get_cart(request)

    try:
        product = Product.objects.get(id=payload.product_id)
    except Product.DoesNotExist:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "장바구니 상품을 찾을수없습니다."
        )
    try:
        cart.add_item(product, payload.quantity)
    except ValidationError as e:
        logger.warning(f"장바구니 상품담기 거부{str(e)}")
        raise HttpError(
            HTTPStatus.NOT_ACCEPTABLE,
            message=e.messages[0]
        )
    return Status(
        HTTPStatus.OK,CommonSuccess(
            message="장바구니 담기성공!!",
            data={
                "mypage_cart_type": cart.mypage_cart_type,
            }
        )
    )


# 장바구니 수량 변경



