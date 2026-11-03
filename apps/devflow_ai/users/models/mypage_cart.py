from django.db import models, transaction
from django.db.models import F# 수정: 수량 동시성 처리용 추가
from django.conf import settings
from django.core.exceptions import ValidationError

NORMAL_MAX_ITEMS = 12      # 일반 장바구니 최대 담기 개수
VIP_MAX_ITEMS = None       # None = 제한 없음
VIP_PURCHASE_THRESHOLD = 10 # 10회 이상 구매 시 VIP

NORMAL_DISCOUNT_RATE = 15
VIP_DISCOUNT_RATE = 20 # VIP 할인율 20%



class MyPageCart(models.Model):

    class MyPageCartType(models.TextChoices):
        NORMAL = "NORMAL", "일반 장바구니"
        VIP_NORMAL = "VIP_NORMAL", "vip_장바구니"  # 수정: 값 앞의 공백 제거

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mypage_cart")
    mypage_cart_type = models.CharField(
        max_length=20,  # 수정: NORMAL_MAX_ITEMS(12)는 길이와 무관한 상수
        choices=MyPageCartType.choices,
        default=MyPageCartType.NORMAL,  # 수정: 기본값 추가 (없으면 생성 시 빈 문자열이 저장됨)
    )
    purchase_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # 수정: 아래 전체를 클래스 안으로 들여쓰기 (기존에는 클래스 밖이었음)
    class Meta:
        verbose_name = '마이페이지'
        verbose_name_plural = '마이페이지 장바구니'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user}-{self.purchase_count}"  # 수정: self.mypage_cart -> self.user


    @property
    def is_vip(self):
        return self.mypage_cart_type == self.MyPageCartType.VIP_NORMAL  # 수정: 비교 대상 오류

    @property
    def max_items(self):
        return VIP_MAX_ITEMS if self.is_vip else NORMAL_MAX_ITEMS  # 수정: NORMAL_DISCOUNT_RATE -> NORMAL_MAX_ITEMS

    @property
    def discount_rate(self):
        return VIP_DISCOUNT_RATE if self.is_vip else NORMAL_DISCOUNT_RATE


    @property
    def total_original_price(self):
        return sum(it.original_total for it in self.items.select_related("product"))

    @property
    def total_discounted_price(self):
        return sum(it.discounted_total for it in self.items.select_related("product", "cart"))

    @transaction.atomic  # 수정: 동시 요청 대비
    def add_item(self,product, quantity=1):
        item = self.items.filter(product=product).first()
        if item :
            item.quantity = F("quantity") + quantity  # 수정: 동시 요청 시 수량 유실 방지
            item.save(update_fields=["quantity"])
            item.refresh_from_db()
            return item

        if self.max_items is not None and self.items.count() >=  self.max_items:
            raise ValidationError(
                f"장바구니는 최대{self.max_items}개 까지 담을수 있습니다."
            )

        return self.items.create(product=product, quantity=quantity)

    # 삭제
    def remove_items(self,item_ids):
       return self.items.filter(id__in=item_ids).delete()


    @transaction.atomic
    def checkout(self, item_ids=None):
        items = self.items.select_related("product")
        if item_ids:
            items = items.filter(id__in=item_ids)
        if not items.exists():
            raise ValidationError("결제할 상품이 없습니다.")
        order = Order.objects.create(user=self.user)
        for it in items:
            OrderItem.objects.create(
                order=order,
                product=it.product,
                quantity=it.quantity,
                original_price=it.unit_price,        # 결제 시점 정가
                price=it.discounted_unit_price,

            )
        items.delete()
        self.purchase_count += 1
        self.upgrade_if_needed()
        self.save()
        return order



    def upgrade_if_needed(self):
        if not self.is_vip and self.purchase_count >= VIP_PURCHASE_THRESHOLD:
            self.mypage_cart_type = self.MyPageCartType.VIP_NORMAL


class CartItem(models.Model):
    cart = models.ForeignKey(MyPageCart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_cart_product")
        ]

    @property
    def unit_price(self):
        """정가 (상품 현재 가격)"""
        return self.product.price

    @property
    def discounted_unit_price(self):
        """할인 적용 단가 (원 단위 내림)"""
        return self.product.price * (100 - self.cart.discount_rate) // 100

    @property
    def original_total(self):
        return self.unit_price * self.quantity

    @property
    def discounted_total(self):
        return self.discounted_unit_price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    original_price = models.PositiveIntegerField()  # 주문 시점 정가(단가)
    price = models.PositiveIntegerField()           # 주문 시점 할인가(단가)