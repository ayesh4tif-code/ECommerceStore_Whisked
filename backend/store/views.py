import json
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Order, OrderItem, Product

# Cake size options and their surcharge. The storefront shows the same labels;
# the server is the source of truth for price.
CAKE_SIZES = {
    "": Decimal("0.00"),
    "6-inch Standard": Decimal("0.00"),
    "8-inch Party (+ $8.00)": Decimal("8.00"),
}
MESSAGE_PLACEMENTS = {"", "Written Directly", "On a Gift Tag"}


def _json_body(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
    if not isinstance(data, dict):
        return None, JsonResponse({"detail": "Request body must be a JSON object."}, status=400)
    return data, None


def _error(message, status=400):
    return JsonResponse({"detail": message}, status=status)


def _product_json(product):
    return {
        "id": product.pk,
        "title": product.title,
        "category": product.category,
        "price": float(product.price),
        "rating": float(product.rating),
        "reviews": product.reviews,
        "image": product.image,
        "hoverImage": product.hover_image,
        "cartImage": product.cart_image or product.image,
        "desc": product.description,
        "specs": product.specs,
    }


@require_GET
@ensure_csrf_cookie
def storefront(request):
    return FileResponse(open(Path(__file__).resolve().parents[2] / "index.html", "rb"))


@require_GET
def products(request):
    return JsonResponse([_product_json(product) for product in Product.objects.filter(is_active=True)], safe=False)


@require_POST
def register(request):
    data, error = _json_body(request)
    if error:
        return error

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not name or len(name) > 150:
        return _error("Please provide a name of 150 characters or fewer.")
    if not email or len(email) > 254:
        return _error("Please provide a valid email address.")
    try:
        validate_email(email)
    except ValidationError:
        return _error("Please provide a valid email address.")
    if not isinstance(password, str):
        return _error("Please provide a valid password.")

    User = get_user_model()
    if User.objects.filter(email__iexact=email).exists():
        return _error("An account with this email already exists.", status=409)
    try:
        validate_password(password)
    except ValidationError as exc:
        return _error(" ".join(exc.messages))

    user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
    login(request, user)
    return JsonResponse({"user": {"name": user.first_name, "email": user.email}}, status=201)


@require_POST
def login_view(request):
    data, error = _json_body(request)
    if error:
        return error

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not email or not isinstance(password, str):
        return _error("Email and password are required.")
    User = get_user_model()
    user_record = User.objects.filter(email__iexact=email).first()
    user = authenticate(request, username=user_record.get_username(), password=password) if user_record else None
    if user is None:
        return _error("Email or password is incorrect.", status=401)
    login(request, user)
    return JsonResponse({"user": {"name": user.first_name or user.get_username(), "email": user.email}})


@require_GET
def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({"user": None})
    return JsonResponse(
        {
            "user": {
                "name": request.user.first_name or request.user.get_username(),
                "email": request.user.email,
            }
        }
    )


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"user": None})


@require_GET
def my_orders(request):
    if not request.user.is_authenticated:
        return _error("Sign in to view your orders.", status=401)

    orders = (
        Order.objects.filter(customer=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return JsonResponse(
        {
            "orders": [
                {
                    "id": order.pk,
                    "status": order.status,
                    "status_label": order.get_status_display(),
                    "fulfillment": order.fulfillment,
                    "address": order.address,
                    "total": float(order.total),
                    "created_at": order.created_at.isoformat(),
                    "items": [
                        {
                            "title": item.product.title,
                            "quantity": item.quantity,
                            "unit_price": float(item.unit_price),
                            "custom_size": item.custom_size,
                        }
                        for item in order.items.all()
                    ],
                }
                for order in orders
            ]
        }
    )


@require_POST
def create_order(request):
    data, error = _json_body(request)
    if error:
        return error

    phone = str(data.get("phone", "")).strip()
    fulfillment = data.get("fulfillment")
    address = str(data.get("address", "")).strip()
    items = data.get("items")
    guest_name = str(data.get("name", "")).strip()
    if not request.user.is_authenticated and (not guest_name or len(guest_name) > 150):
        return _error("Please provide your name (150 characters or fewer).")
    if not phone or len(phone) > 40:
        return _error("Please provide a valid phone number.")
    if fulfillment not in {Order.DELIVERY, Order.PICKUP}:
        return _error("Fulfillment must be delivery or pickup.")
    if fulfillment == Order.DELIVERY and (not address or len(address) > 300):
        return _error("A delivery address of 300 characters or fewer is required.")
    if not isinstance(items, list) or not items or len(items) > 50:
        return _error("Your order must contain between 1 and 50 line items.")

    validated_items = []
    total = Decimal("0.00")
    for item in items:
        if not isinstance(item, dict):
            return _error("Each order item must be an object.")
        try:
            product_id = int(item.get("product_id"))
            quantity = int(item.get("quantity"))
        except (TypeError, ValueError):
            return _error("Each item needs a valid product and quantity.")
        if quantity < 1 or quantity > 99:
            return _error("Item quantities must be between 1 and 99.")
        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if product is None:
            return _error(f"Product {product_id} is unavailable.", status=404)

        custom_size = str(item.get("custom_size", "")).strip()
        if product.category == "Cakes":
            if custom_size not in CAKE_SIZES:
                return _error(f"Invalid cake size for {product.title}.")
        elif custom_size:
            return _error(f"{product.title} does not support size customization.")
        message_type = str(item.get("custom_message_type", "")).strip()
        if message_type not in MESSAGE_PLACEMENTS:
            return _error("Invalid custom message placement.")
        message = str(item.get("custom_message", "")).strip()
        note = str(item.get("note", "")).strip()
        if len(message) > 200 or len(note) > 200:
            return _error("Custom messages and notes must be 200 characters or fewer.")

        unit_price = product.price + CAKE_SIZES.get(custom_size, Decimal("0.00"))
        total += unit_price * quantity
        validated_items.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "custom_size": custom_size,
                "custom_message_type": message_type,
                "custom_message": message,
                "note": note,
            }
        )

    user = request.user if request.user.is_authenticated else None
    with transaction.atomic():
        order = Order.objects.create(
            customer=user,
            customer_name=user.first_name if user else guest_name,
            email=user.email if user else "",
            phone=phone,
            fulfillment=fulfillment,
            address=address if fulfillment == Order.DELIVERY else "",
            total=total,
        )
        OrderItem.objects.bulk_create(
            [OrderItem(order=order, **item) for item in validated_items]
        )

    return JsonResponse(
        {
            "id": order.pk,
            "total": float(order.total),
            "status": order.status,
            "created_at": order.created_at.isoformat(),
        },
        status=201,
    )
