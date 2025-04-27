from django.urls import path

from . import views
from .views import createMarketPost, makeOffer, deleteOffer

urlpatterns = [
    path("", views.index, name="index"),
    path('create/', createMarketPost, name='createMarketPost'),
    path('make_offer/<int:post_id>/', makeOffer, name='make_offer'),
    path('delete_offer/', views.deleteOffer, name='delete_offer'),
]
