from zoneinfo import available_timezones

from django.db.models.sql.query import get_order_dir
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Collection.models import Pokemon
from marketplace.models import MarketPost
from .models import TradeOffer
from .models import Transaction

# Create your views here.
@login_required
def trade_pokemon(request, pokemon_name):
    offered_pokemon = get_object_or_404(Pokemon, name=pokemon_name, owner=request.user)
    user_pokemons = Pokemon.objects.filter(owner=request.user)

    available_pokemons = Pokemon.objects.exclude(owner=request.user, name=offered_pokemon.name)

    if request.method == 'POST':
        requested_pokemon_detail = request.POST.get('requested_pokemon')
        gold_amount = request.POST.get('gold')

        requested_pokemon = None
        if requested_pokemon_detail:
            requested_pokemon = Pokemon.objects.filter(name=requested_pokemon_detail).first()

        if requested_pokemon_detail and not requested_pokemon:
            messages.error(request, 'Requested Pokémon not found. Please enter a valid Pokémon name.')
            return redirect('trading.trade_pokemon', pokemon_name=offered_pokemon.name)

        if not requested_pokemon and not gold_amount:
            messages.error(request, 'Please specify either a Pokemon or an amount of gold.')
            return redirect('trading.trading_pokemon', pokemon_name=offered_pokemon)

        if gold_amount:
            if not gold_amount.isdigit() or int(gold_amount) <= 0:
                messages.error(request, 'Gold amount must be a valid positive number.')
                return redirect('trading.trading_pokemon', pokemon_name=offered_pokemon)
            gold_amount = int(gold_amount)

        market_post, created = MarketPost.objects.get_or_create(
            user = request.user,
            pokemon = offered_pokemon,
            requested_pokemon = requested_pokemon,
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
                                                 'user_pokemons': user_pokemons, 'available_pokemons': available_pokemons})

def trade_offers(request):
    return render(request, 'trading/negotiations.html', {'trade_offers': trade_offers})

def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'trading/transaction_history.html', {'transactions': transactions})
