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

    available_pokemons = Pokemon.objects.exclude(owner=request.user).exclude(name=offered_pokemon.name)

    existing_trade_offer = TradeOffer.objects.filter(user=request.user, pokemon_offered=offered_pokemon).exists()

    if existing_trade_offer:
        # Redirect to collection index with an error message
        messages.error(request, 'You already have an active trade offer with this Pokémon.')
        return redirect('Collection.index')

    if request.method == 'POST':
        requested_pokemon_detail = request.POST.get('requested_pokemon')
        gold_amount = request.POST.get('gold')

        requested_pokemon = None
        if requested_pokemon_detail:
            requested_pokemon = Pokemon.objects.filter(name=requested_pokemon_detail).first()
            if not requested_pokemon:
                messages.error(request, 'Requested Pokémon not found. Please select a valid Pokémon.')
                return render(request, 'trading/create_trade.html', {
                    'offered_pokemon': offered_pokemon,
                    'user_pokemons': user_pokemons,
                    'available_pokemons': available_pokemons
                })

        if not requested_pokemon and not gold_amount:
            messages.error(request, 'Please specify either a Pokémon or an amount of gold.')
            return render(request, 'trading/create_trade.html', {
                'offered_pokemon': offered_pokemon,
                'user_pokemons': user_pokemons,
                'available_pokemons': available_pokemons
            })

        if gold_amount:
            if not gold_amount.isdigit() or int(gold_amount) <= 0:
                messages.error(request, 'Gold amount must be a valid positive number.')
                return render(request, 'trading/create_trade.html', {
                    'offered_pokemon': offered_pokemon,
                    'user_pokemons': user_pokemons,
                    'available_pokemons': available_pokemons
                })
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

def acceptOffer(request, post_id):
    offer = get_object_or_404(MarketPost, id=post_id)

    if offer.user == request.user:
        messages.error(request, "You cannot accept your offer.")
        return redirect('marketplace.index')

    offered_pokemon = offer.pokemon
    requested_pokemon = offer.requested_pokemon

    requested_pokemon_owner = requested_pokemon.owner
    offered_pokemon_owner = offered_pokemon.owner

    if requested_pokemon_owner != request.user:
        messages.error(request, "You don't have the requested Pokemon to complete the trade.")
        return redirect('marketplace.index')

    gold_amount = offer.gold if offer.gold else 0

    with transaction.atomic():
        offered_pokemon.owner = requested_pokemon_owner
        requested_pokemon.owner = offered_pokemon_owner

        offered_pokemon.save()
        requested_pokemon.save()

        Transaction.objects.create(
            user = offered_pokemon_owner,
            transaction_type = "trade",
            pokemon_offered = offered_pokemon,
            pokemon_received = requested_pokemon,
            gold_offered = gold_amount,
            gold_received = None,
        )

        Transaction.objects.create(
            user = offered_pokemon_owner,
            transaction_type = "trade",
            pokemon_offered = offered_pokemon,
            pokemon_received = requested_pokemon,
            gold_offered = None,
            gold_received = gold_amount,
        )

        offer.delete()

    return redirect('marketplace.index')

def trade_offers(request):
    return render(request, 'trading/negotiations.html', {'trade_offers': trade_offers})

def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'trading/transaction_history.html', {'transactions': transactions})
