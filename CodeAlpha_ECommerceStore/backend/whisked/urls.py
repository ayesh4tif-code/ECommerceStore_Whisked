from django.contrib import admin
from django.urls import include, path

from store.views import storefront


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("store.urls")),
    path("", storefront, name="storefront"),
]
