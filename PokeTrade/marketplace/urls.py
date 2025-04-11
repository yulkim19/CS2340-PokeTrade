from django.urls import path

from . import views
from .views import createMarketPost, makeOffer

urlpatterns = [
    path("", views.index, name="index"),
    path('create/', createMarketPost, name='createMarketPost'),
    path('offer/', makeOffer, name='makeOffer'),
]
