from .models import MarketPost, TradeOffer
from PokeTrade.Collection.models import Pokemon
from django.contrib.auth.models import User


def createMarketPost(user, pokemon):
    MarketPost.objects.create(user=user, pokemon=pokemon, time_remaining=120)


def createTradeOffer(offer, user, pokemon=None, gold=None):
    TradeOffer.objects.create(user=user, offer=offer, pokemon=pokemon, gold=gold)
