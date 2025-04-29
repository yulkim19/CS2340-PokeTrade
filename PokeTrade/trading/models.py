# trading/models.py

from django.db import models
from django.contrib.auth.models import User
from Collection.models import Pokemon
from marketplace.models import MarketPost

class TradeOffer(models.Model):
    sender    = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_trade_offers'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_trade_offers'
    )
    offer     = models.ForeignKey(
        MarketPost,
        on_delete=models.CASCADE,
        related_name='trade_offers'
    )

    pokemon_offered   = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='trade_offers_offered',
        null=True,
        blank=True
    )
    pokemon_requested = models.ForeignKey(
        Pokemon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trade_offers_requested'
    )
    gold = models.IntegerField(null=True, blank=True)

    def __str__(self):
        parts = []
        # Who’s giving what:
        if self.pokemon_offered:
            parts.append(f"{self.pokemon_offered.name}")
        if self.gold:
            parts.append(f"{self.gold} gold")
        give = " + ".join(parts) or "Nothing"

        # Who’s getting what:
        want = (self.pokemon_requested.name
                if self.pokemon_requested else "Gold")

        return f"Offer #{self.id}: {self.sender.username} gives {give} for {want} (to {self.recipient.username})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('trade', 'Trade'),
        ('sale',  'Sale'),
    ]

    user              = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    pokemon           = models.ForeignKey(
        Pokemon,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    transaction_type  = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )
    received_gold     = models.PositiveIntegerField(null=True, blank=True)
    traded_with       = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='received_transactions'
    )
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        what = self.pokemon.name if self.pokemon else f"{self.received_gold} gold"
        return f"{self.user.username} {self.transaction_type}d {what}"
