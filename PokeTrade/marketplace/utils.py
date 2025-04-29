# marketplace/utils.py

from .models import MarketPost, TradeOffer

def createMarketPost(user, pokemon):
    """
    List a Pokémon on the marketplace. Does NOT create a TradeOffer.
    """
    MarketPost.objects.create(
        user=user,
        pokemon=pokemon,
        time_remaining=1200
    )

def createTradeOffer(market_post, sender, offered_pokemon=None, gold=None):
    """
    Make a trade offer on an existing MarketPost.
    """
    TradeOffer.objects.create(
        sender=sender,
        recipient=market_post.user,
        offer=market_post,
        pokemon_offered=offered_pokemon,
        pokemon_requested=market_post.pokemon,
        gold=gold
    )
