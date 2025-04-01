from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("Collection/", include("Collection.urls")),
    path("admin/", admin.site.urls),
]
