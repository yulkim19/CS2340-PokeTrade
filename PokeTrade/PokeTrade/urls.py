from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path("Collection/", include("Collection.urls")),
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
