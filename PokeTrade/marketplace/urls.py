from django.urls import path

from . import views
from .views import createMarketPost, makeOffer, deleteOffer

urlpatterns = [
    path("", views.index, name="index"),
    path('create/', createMarketPost, name='createMarketPost'),
    path('offer/', makeOffer, name='makeOffer'),
    path('delete_offer/', views.deleteOffer, name='delete_offer')
]
