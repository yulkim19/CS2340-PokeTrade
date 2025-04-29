from django.urls import path
from . import views

urlpatterns = [
    path(
        "create_trade/<str:pokemon_name>/",
        views.trade_pokemon,
        name="trade_pokemon"
    ),
    path(
        "trade_offers/",
        views.trade_offers,
        name="trade_offers"
    ),
    path(
        "history/",
        views.transaction_history,
        name="transaction_history"
    ),
    path(
        "accept_offer/<int:offer_id>/",
        views.accept_offer,
        name="accept_offer"
    ),
    path(
        "decline_offer/<int:offer_id>/",
        views.decline_offer,
        name="decline_offer"
    ),
]
