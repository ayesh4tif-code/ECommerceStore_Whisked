from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price", "custom_size", "custom_message", "note")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "fulfillment", "total", "status", "created_at")
    list_filter = ("status", "fulfillment", "created_at")
    search_fields = ("id", "customer_name", "email", "phone")
    list_editable = ("status",)
    inlines = [OrderItemInline]
