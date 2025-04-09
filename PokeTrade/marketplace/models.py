from django.db import models
from django.contrib.auth.models import User
from PokeTrade.Collection.models import Pokemon

# Create your models here.
class MarketPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    price = models.IntegerField()