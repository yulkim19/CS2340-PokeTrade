from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Pokemon(models.Model):
    pokedex = models.IntegerField()
    name = models.CharField(max_length=50)
    primary_type = models.CharField(max_length=50)
    secondary_type = models.CharField(max_length=50)
    sprite = models.CharField(max_length=200)
    pkdex = models.CharField(max_length=400)
    rarity = models.IntegerField()
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pokemons"  # This allows you to do user.pokemons.all()
    )


    def __str__(self):
        return self.name