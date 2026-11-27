import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0002_remove_product_name_product_is_trainee_only_and_more"),
        ("users", "0004_alter_signupuser_user_position_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MyPageCart",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mypage_cart_type", models.CharField(choices=[("NORMAL", "일반 장바구니"), ("VIP_NORMAL", "vip_장바구니")], default="NORMAL", max_length=20)),
                ("purchase_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="mypage_cart", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "마이페이지",
                "verbose_name_plural": "마이페이지 장바구니",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cart", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="users.mypagecart")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="product.product")),
            ],
            options={
                "constraints": [models.UniqueConstraint(fields=("cart", "product"), name="unique_cart_product")],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField()),
                ("original_price", models.PositiveIntegerField()),
                ("price", models.PositiveIntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="users.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="product.product")),
            ],
        ),
    ]
