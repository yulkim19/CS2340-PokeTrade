from .models import MarketPost, TradeOffer


def createMarketPost(user, pokemon):
    MarketPost.objects.create(user=user, pokemon=pokemon, time_remaining=120)


def createTradeOffer(offer, user, pokemon=None, gold=None):
    TradeOffer.objects.create(user=user, offer=offer, pokemon=pokemon, gold=gold)
