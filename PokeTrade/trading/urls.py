from django.urls import path
from . import views

urlpatterns = [
    path("create_trade/<str:pokemon_name>/", views.trade_pokemon, name="trading.trade_pokemon"),
    path("trade_offers/", views.trade_offers, name="trading.trade_offers"),
    path("history/", views.transaction_history, name="trading.transaction_history"),
    path('accept_offer/<int:post_id>/', views.acceptOffer, name='accept_offer'),
]