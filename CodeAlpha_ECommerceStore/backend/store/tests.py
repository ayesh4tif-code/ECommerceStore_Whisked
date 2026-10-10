import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Order, Product


class StoreApiTests(TestCase):
    def setUp(self):
        self.cake = Product.objects.create(
            title="Vanilla Cake",
            category="Cakes",
            price=Decimal("28.50"),
            image="https://example.com/cake.jpg",
            description="A vanilla cake.",
            specs=[],
        )

    def test_products_returns_catalog_fields_used_by_storefront(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        product = response.json()[0]
        self.assertEqual(product["id"], self.cake.pk)
        self.assertEqual(product["price"], 28.5)
        self.assertEqual(product["desc"], "A vanilla cake.")
        self.assertEqual(product["cartImage"], self.cake.image)

    def test_current_user_returns_empty_session_for_signed_out_visitor(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["user"])

    def test_order_uses_database_price_and_persists_customization(self):
        response = self.client.post(
            "/api/orders/",
            data=json.dumps(
                {
                    "phone": "+92 300 1234567",
                    "fulfillment": "delivery",
                    "address": "Street 12",
                    "items": [
                        {
                            "product_id": self.cake.pk,
                            "quantity": 2,
                            "price": 0,
                            "custom_size": "8-inch Party (+ $8.00)",
                            "custom_message_type": "On a Gift Tag",
                            "custom_message": "Happy birthday!",
                            "note": "No nuts",
                        }
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["total"], 73.0)
        order = Order.objects.get(pk=response.json()["id"])
        self.assertIsNone(order.customer)
        self.assertEqual(order.status, Order.RECEIVED)
        self.assertEqual(order.items.get().unit_price, Decimal("36.50"))
        self.assertEqual(order.items.get().custom_message, "Happy birthday!")

    def test_signed_in_order_is_linked_and_appears_only_in_that_users_tracking(self):
        User = get_user_model()
        customer = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="A-long-unique-password-2026",
            first_name="Customer",
        )
        another_customer = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="A-long-unique-password-2026",
        )
        self.client.force_login(customer)
        response = self.client.post(
            "/api/orders/",
            data=json.dumps(
                {
                    "phone": "03001234567",
                    "fulfillment": "pickup",
                    "items": [{"product_id": self.cake.pk, "quantity": 1}],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(pk=response.json()["id"])
        self.assertEqual(order.customer, customer)
        order.status = Order.BAKING
        order.save(update_fields=["status"])

        tracking = self.client.get("/api/orders/mine/")
        self.assertEqual(tracking.status_code, 200)
        self.assertEqual(len(tracking.json()["orders"]), 1)
        self.assertEqual(tracking.json()["orders"][0]["status"], Order.BAKING)
        self.assertEqual(tracking.json()["orders"][0]["items"][0]["title"], self.cake.title)

        self.client.force_login(another_customer)
        self.assertEqual(self.client.get("/api/orders/mine/").json()["orders"], [])

    def test_order_tracking_requires_an_account(self):
        response = self.client.get("/api/orders/mine/")

        self.assertEqual(response.status_code, 401)

    def test_delivery_order_requires_address(self):
        response = self.client.post(
            "/api/orders/",
            data=json.dumps(
                {
                    "phone": "03001234567",
                    "fulfillment": "delivery",
                    "items": [{"product_id": self.cake.pk, "quantity": 1}],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_register_and_login_use_django_session_authentication(self):
        credentials = {
            "name": "Ayesha Baker",
            "email": "ayesha@example.com",
            "password": "A-long-unique-password-2026",
        }
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(credentials),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get("/api/auth/me/").json()["user"]["name"], "Ayesha Baker")

        self.client.logout()
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"email": credentials["email"], "password": credentials["password"]}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me/").json()["user"]["email"], credentials["email"])

        response = self.client.post(
            "/api/auth/logout/",
            data="{}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.get("/api/auth/me/").json()["user"])
