from django.urls import path

from . import views


urlpatterns = [
    path("products/", views.products, name="products"),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/me/", views.current_user, name="current-user"),
    path("orders/", views.create_order, name="create-order"),
    path("orders/mine/", views.my_orders, name="my-orders"),
]
