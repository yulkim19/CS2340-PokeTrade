from django.db import models
from django.contrib.auth.models import User
from Collection.models import Pokemon
from marketplace.models import MarketPost

class TradeOffer(models.Model):
    sender    = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='sent_trade_offers')
    recipient = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='received_trade_offers')
    offer     = models.ForeignKey(MarketPost,
                                  on_delete=models.CASCADE,
                                  related_name='trade_offers')
    pokemon_offered   = models.ForeignKey(Pokemon,
                                          on_delete=models.CASCADE,
                                          related_name='trade_offers_offered')
    pokemon_requested = models.ForeignKey(Pokemon,
                                          on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='trade_offers_requested')
    gold = models.IntegerField(null=True, blank=True)

    def __str__(self):
        requested = (self.pokemon_requested.name
                     if self.pokemon_requested else f"{self.gold} Gold")
        return (
            f"Offer #{self.id} from {self.sender.username} to {self.recipient.username}: "
            f"{self.pokemon_offered.name} → {requested}"
        )

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('trade', 'Trade'),
        ('sale',  'Sale'),
    ]

    user              = models.ForeignKey(User,
                                          on_delete=models.CASCADE,
                                          related_name='transactions')
    pokemon           = models.ForeignKey(Pokemon,
                                          on_delete=models.SET_NULL,
                                          null=True, blank=True)
    transaction_type  = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    received_gold     = models.PositiveIntegerField(null=True, blank=True)
    traded_with       = models.ForeignKey(User,
                                          on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='received_transactions')
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        what = self.pokemon.name if self.pokemon else 'Gold'
        return f"{self.user.username} {self.transaction_type}d {what}"

    def clean(self):
        if self.transaction_type == 'trade' and not self.pokemon:
            raise models.ValidationError("A Pokémon must be associated with a trade.")
        if self.transaction_type == 'sale' and not self.received_gold:
            raise models.ValidationError("Gold must be received for a sale.")
