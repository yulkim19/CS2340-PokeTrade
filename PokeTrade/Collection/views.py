from django.http import HttpResponse
from django.shortcuts import render, redirect
from .utils import generateRandomPokemon
from .models import Pokemon

def index(request):
    pokemons = Pokemon.objects.filter(owner=0) #EDIT THIS LATER
    context = {
        'pokemons': pokemons,
    }
    return render(request, "collection/collectionview.html", context)

def about(request):
    return HttpResponse("Welcome to the About Page")

def generate_pokemon_view(request):
    if request.method == "POST":
        # Use the current user (or Trainer) to generate and add a Pokemon.
        generateRandomPokemon(request.user)
        # Optionally, you can add a Django message here.
        return redirect('Collection.index')  # Redirect to the collection page (or wherever you like)
    # If it's not a POST, just redirect.
    return redirect('Collection.index')

