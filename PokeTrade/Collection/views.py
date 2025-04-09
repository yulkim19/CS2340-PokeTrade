from django.http import HttpResponse
from django.shortcuts import render, redirect
from .utils import generateRandomPokemon
from .models import Pokemon


def index(request):
    pokemons = Pokemon.objects.filter(owner=request.user)  #EDIT THIS LATER
    context = {
        'pokemons': pokemons,
    }
    return render(request, "collection/collectionview.html", context)


def about(request):
    return HttpResponse("Welcome to the About Page")


def generate_pokemon_view(request):
    if request.method == "POST":
        generateRandomPokemon(request.user)
        return redirect('Collection.index')
    return redirect('Collection.index')
