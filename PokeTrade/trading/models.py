from django.db import models
from django.contrib.auth.models import User
from Collection.models import Pokemon
from marketplace.models import MarketPost

# Create your models here.
class TradeOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trade_offers_user')
    offer = models.ForeignKey(MarketPost, on_delete=models.CASCADE, related_name='trade_offers')
    pokemon_offered = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='trade_offers_offered')
    pokemon_requested = models.ForeignKey(Pokemon, on_delete=models.SET_NULL, null=True, blank=True, related_name='trade_offers_requested')
    gold = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (f"Trade Offer by {self.user.username} (Offer: {self.pokemon_offered} "
                f"for {self.pokemon_requested or 'Gold'})")