from django.urls import path
from . import views

urlpatterns = [
    path("create_trade/<str:pokemon_name>/", views.trade_pokemon, name="trading.trade_pokemon"),
]