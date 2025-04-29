from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Pokemon
from .utils import generateRandomPokemon, get_or_create_background

# Static list of all Pokémon types (must match your utils’ TYPE_PROMPTS keys)
POKEMON_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

@login_required
def index(request):
    pokemons = Pokemon.objects.filter(owner=request.user)

    # 1️⃣ Read filters from GET params
    type_filter = request.GET.get('type', '')
    rarity_filter = request.GET.get('rarity', '')

    # 2️⃣ Apply filters if present
    if type_filter:
        pokemons = pokemons.filter(primary_type__iexact=type_filter)
    if rarity_filter:
        try:
            rarity_val = int(rarity_filter)
            pokemons = pokemons.filter(rarity=rarity_val)
        except ValueError:
            pass

    # 3️⃣ Attach background_url
    for p in pokemons:
        p.background_url = get_or_create_background(p)

    # 4️⃣ Pass filters & choices into context
    context = {
        'pokemons': pokemons,
        'filter_type': type_filter,
        'filter_rarity': rarity_filter,
        'types': POKEMON_TYPES,
        'rarities': range(1, 8),
    }
    return render(request, "collection/collectionview.html", context)

@login_required
def generate_pokemon_view(request):
    if request.method == "POST":
        generateRandomPokemon(request.user)
    return redirect('Collection.index')
