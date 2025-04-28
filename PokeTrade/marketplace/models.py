from django.db import models
from django.contrib.auth.models import User
from Collection.models import Pokemon


# Create your models here.
class MarketPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE,
                                related_name='offered_pokemon_set')
    requested_pokemon = models.ForeignKey(Pokemon, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='requested_pokemon_set')
    gold = models.IntegerField(null=True, blank=True)
    time_remaining = models.IntegerField()

    def __str__(self):
        return f"MarketPost by {self.user.username} - Offering {self.pokemon.name} for {self.requested_pokemon.name if self.requested_pokemon else 'Gold'}"


class TradeOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ForeignKey(MarketPost, on_delete=models.CASCADE)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, null=True)
    gold = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (f"Trade Offer by {self.user.username} (Offer: {self.pokemon_offered.name} "
                f"for {self.pokemon_requested.name if self.pokemon_requested else 'Gold'})")

    def clean(self):
        # Ensure that either a Pokémon or gold is requested
        if not self.pokemon_requested and not self.gold:
            raise models.ValidationError("Please specify either a Pokémon or gold to request.")

        # Optional: Add custom save method to handle post-trade actions (e.g., creating a transaction)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
