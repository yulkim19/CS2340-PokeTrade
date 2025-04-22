from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Collection.models import Pokemon
from marketplace.models import MarketPost
from .models import TradeOffer

# Create your views here.
@login_required
def trade_pokemon(request, pokemon_name):
    offered_pokemon = get_object_or_404(Pokemon, name=pokemon_name, owner=request.user)
    user_pokemons = Pokemon.objects.filter(owner=request.user)

    if request.method == 'POST':
        requested_pokemon_detail = request.POST.get('requested_pokemon')
        gold_amount = request.POST.get('gold')

        requested_pokemon = None
        if requested_pokemon_detail:
            requested_pokemon = Pokemon.objects.filter(name=requested_pokemon_detail).first()

        market_post, created = MarketPost.objects.get_or_create(
            user = request.user,
            pokemon = offered_pokemon,
            defaults={'time_remaining': 1000}
        )

        trade_offer = TradeOffer.objects.create(
            user = request.user,
            offer = market_post,
            pokemon_offered = offered_pokemon,
            pokemon_requested = requested_pokemon,
            gold = gold_amount if gold_amount else None
        )

        return redirect('Collection.index')
    return render(request, 'trading/create_trade.html', {'offered_pokemon': offered_pokemon,
                                                 'user_pokemons': user_pokemons})
