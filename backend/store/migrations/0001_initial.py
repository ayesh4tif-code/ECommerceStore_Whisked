import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("category", models.CharField(max_length=40)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("rating", models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ("reviews", models.PositiveIntegerField(default=0)),
                ("image", models.URLField(max_length=500)),
                ("hover_image", models.URLField(blank=True, max_length=500)),
                ("cart_image", models.URLField(blank=True, max_length=500)),
                ("description", models.TextField()),
                ("specs", models.JSONField(default=list)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(blank=True, max_length=150)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(max_length=40)),
                ("fulfillment", models.CharField(choices=[("delivery", "Delivery"), ("pickup", "Store pickup")], max_length=10)),
                ("address", models.CharField(blank=True, max_length=300)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("received", "Received")], default="received", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("customer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="store_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveSmallIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("custom_size", models.CharField(blank=True, max_length=60)),
                ("custom_message_type", models.CharField(blank=True, max_length=40)),
                ("custom_message", models.CharField(blank=True, max_length=200)),
                ("note", models.CharField(blank=True, max_length=200)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="store.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="store.product")),
            ],
        ),
    ]
