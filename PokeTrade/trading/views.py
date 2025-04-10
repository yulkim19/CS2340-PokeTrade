from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Collection.models import Pokemon
from marketplace.models import MarketPost
from .models import TradeOffer

# Create your views here.
@login_required
def trade_pokemon(request, pokemon_name):
    offered_pokemon = Pokemon.objects.get(name=pokemon_name, owner=request.user)
    user_pokemons = Pokemon.objects.filter(owner=request.user)

    if request.method == 'POST':
        requested_pokemon_detail = request.POST.get('requested_pokemon')
        gold_amount = request.POST.get('gold')

        requested_pokemon = None
        if requested_pokemon_detail:
            requested_pokemon = Pokemon.objects.filter(name=requested_pokemon_detail).first()

        offered_pokemon_detail = request.POST.get('offered_pokemon')
        offered_pokemon = Pokemon.objects.filter(name=offered_pokemon_detail, owner=request.user).first()

        trade_offer = TradeOffer.objects.create(
            user = request.user,
            pokemon_offered = offered_pokemon,
            pokemon_requested = requested_pokemon,
            gold = gold_amount if gold_amount else None
        )
        return redirect('Collection.index')
    return render(request, 'create_trade.html', {'offered_pokemon': offered_pokemon,
                                                 'user_pokemons': user_pokemons})
