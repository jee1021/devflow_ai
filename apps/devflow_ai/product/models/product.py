import calendar


from django.db import models, transaction
from django.conf import settings
from django.utils import timezone

FEATURES_BY_PLAN = {
    "PLANNER": ["PLANNER"],
    "SLACK": ["SLACK"],
    "BUNDLE": ["PLANNER", "SLACK"],
}


class RedeemError(Exception):
    pass

def is_trainee(user):
    return bool(getattr(user, "is_trainee", False))

class Product(models.Model):
    price = models.PositiveIntegerField()
    period_months = models.PositiveIntegerField(default=1)
    plan_type = models.CharField(
        max_length=20,
        choices=[
            ("PLANNER", "PLANNER"),
            ("SLACK", "SLACK"),
            ("BUNDLE", "BUNDLE"),
        ]
    )
    required_points = models.PositiveIntegerField(
        default=0, help_text="0이면 일반 상품. 1 이상이면 출석 포인트로 결제하는 상품"
    )
    is_trainee_only = models.BooleanField(
        default=False, help_text="예비개발자 전용 상품 여부"
    )

    def __str__(self):
        return self.name


@staticmethod
def add_months(year, month):
    index = dt.month - 1 + month
    year = dt.year + index // 12
    month = index % 12 + 1
    day = min(dt.day, calendar.month(year, month)[1])
    return dt.replace(year=year, month=month, day=day)



class PointRedemption(models.Model):
    """포인트 결제 이력. (user, product) 유니크라 상품당 1회만 교환 가능."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="redemptions"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    points_used = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_redemption")
        ]

    def __str__(self):
        return f"{self.user}-{self.product}-{self.points_used}"
# ▲ 추가


class AttendancePoint:
    pass


class UserPass(models.Model):
    """사용자별 이용권. 기능(feature)마다 한 줄이고, expires_at까지 사용 가능."""

    class Feature(models.TextChoices):
        PLANNER = "PLANNER", "플래너(일정)"
        SLACK = "SLACK", "슬랙 메시지"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="passes"
    )
    feature = models.CharField(max_length=20, choices=Feature.choices)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "이용권"
        verbose_name_plural = "이용권"
        constraints = [
            models.UniqueConstraint(fields=["user", "feature"], name="unique_user_feature")
        ]

    def __str__(self):
        return f"{self.user}-{self.feature}-{self.expires_at:%Y-%m-%d}"

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    @classmethod
    def has_active(cls, user, feature):
        """이 기능의 유효한 이용권이 있는가 (만료는 조회 시점에 계산)"""
        if not user.is_authenticated:
            return False
        return cls.objects.filter(
            user=user, feature=feature, expires_at__gt=timezone.now()
        ).exists()

    @classmethod
    @transaction.atomic
    def grant(cls, user, product, quantity=1):
        """결제 확정된 상품으로 이용권 지급/연장. 남은 기간이 있으면 만료일부터 이어 붙인다."""
        now = timezone.now()
        months = product.period_months * quantity
        for feature in FEATURES_BY_PLAN[product.plan_type]:
            obj, _ = cls.objects.select_for_update().get_or_create(
                user=user, feature=feature, defaults={"expires_at": now}
            )
            obj.expires_at = Product.add_months(max(obj.expires_at, now), months)  # ← 수정
            obj.save(update_fields=["expires_at", "updated_at"])

    # ▼ 추가
    @classmethod
    @transaction.atomic
    def redeem_with_points(cls, user, product):
        """출석 포인트로 상품 결제(교환). 조건을 만족하면 이용권을 지급한다."""
        if product.required_points <= 0:
            raise RedeemError("포인트로 교환할 수 없는 상품입니다.")
        if product.is_trainee_only and not is_trainee(user):
            raise RedeemError("예비개발자만 신청할 수 있는 상품입니다.")

        # 동시 요청으로 포인트가 중복 차감되지 않도록 유저 행을 잠근다
        type(user).objects.select_for_update().get(pk=user.pk)

        if PointRedemption.objects.filter(user=user, product=product).exists():
            raise RedeemError("이미 교환한 상품입니다.")
        if AttendancePoint.balance(user) < product.required_points:
            raise RedeemError("출석 포인트가 부족합니다.")

        AttendancePoint.objects.create(
            user=user, points=-product.required_points, reason=f"{product.name} 교환"
        )
        PointRedemption.objects.create(
            user=user, product=product, points_used=product.required_points
        )
        cls.grant(user, product)  # 기존 로직 재사용 (남은 기간 이어 붙이기 포함)
    # ▲ 추가
class AttendancePoint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_points",
    )
    points = models.IntegerField()
    reason = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "출석 포인트"
        verbose_name_plural = "출석 포인트"

    def __str__(self):
        return f"{self.user}-{self.points:+d}({self.reason})"

    @classmethod
    def balance(cls, user):
        return cls.objects.filter(user=user).aggregate(total=models.Sum("points"))["total"] or 0