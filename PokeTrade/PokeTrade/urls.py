from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path("collection/", include("Collection.urls")),
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('trading/', include('trading.urls')),
    path('chats/', include('chats.urls')),
    path('about/', views.about, name='about'),
    path('', include('home.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
