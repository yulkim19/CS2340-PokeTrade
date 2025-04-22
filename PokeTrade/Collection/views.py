from django.http import HttpResponse
from django.shortcuts import render, redirect
from .utils import generateRandomPokemon
from .models import Pokemon
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    pokemons = Pokemon.objects.filter(owner=request.user)  #EDIT THIS LATER
    context = {
        'pokemons': pokemons,
    }
    return render(request, "collection/collectionview.html", context)

@login_required
def generate_pokemon_view(request):
    if request.method == "POST":
        generateRandomPokemon(request.user)
        return redirect('Collection.index')
    return redirect('Collection.index')
