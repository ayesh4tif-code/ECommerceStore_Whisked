from django.conf import settings
from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    reviews = models.PositiveIntegerField(default=0)
    image = models.URLField(max_length=500)
    hover_image = models.URLField(max_length=500, blank=True)
    cart_image = models.URLField(max_length=500, blank=True)
    description = models.TextField()
    specs = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class Order(models.Model):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    FULFILLMENT_CHOICES = [
        (DELIVERY, "Delivery"),
        (PICKUP, "Store pickup"),
    ]
    RECEIVED = "received"
    BAKING = "baking"
    READY = "ready"
    COMPLETED = "completed"
    STATUS_CHOICES = [
        (RECEIVED, "Received"),
        (BAKING, "Baking"),
        (READY, "Ready"),
        (COMPLETED, "Completed"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="store_orders",
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40)
    fulfillment = models.CharField(max_length=10, choices=FULFILLMENT_CHOICES)
    address = models.CharField(max_length=300, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=RECEIVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    custom_size = models.CharField(max_length=60, blank=True)
    custom_message_type = models.CharField(max_length=40, blank=True)
    custom_message = models.CharField(max_length=200, blank=True)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"
