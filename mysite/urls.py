from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("flagai.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]