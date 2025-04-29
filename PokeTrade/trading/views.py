from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from Collection.models import Pokemon
from marketplace.models import MarketPost
from .models import TradeOffer, Transaction

@login_required
def trade_pokemon(request, pokemon_name):
    offered_pokemon = get_object_or_404(
        Pokemon, name=pokemon_name, owner=request.user
    )
    user_pokemons = Pokemon.objects.filter(owner=request.user)
    available_pokemons = Pokemon.objects.exclude(
        owner=request.user
    ).exclude(name=offered_pokemon.name)

    if TradeOffer.objects.filter(
        sender=request.user,
        pokemon_offered=offered_pokemon
    ).exists():
        messages.error(request,
            "You already have an active trade offer with this Pokémon."
        )
        return redirect('Collection.index')

    if request.method == 'POST':
        requested_name = request.POST.get('requested_pokemon')
        gold_amount    = request.POST.get('gold')

        requested_pokemon = None
        if requested_name:
            requested_pokemon = Pokemon.objects.filter(
                name=requested_name
            ).first()
            if not requested_pokemon:
                messages.error(request,
                    "Requested Pokémon not found."
                )
                return render(request, 'trading/create_trade.html', {
                    'offered_pokemon':   offered_pokemon,
                    'user_pokemons':     user_pokemons,
                    'available_pokemons':available_pokemons
                })

        if not requested_pokemon and not gold_amount:
            messages.error(request,
                "Please specify either a Pokémon or an amount of gold."
            )
            return render(request, 'trading/create_trade.html', {
                'offered_pokemon':   offered_pokemon,
                'user_pokemons':     user_pokemons,
                'available_pokemons':available_pokemons
            })
        if gold_amount:
            if not gold_amount.isdigit() or int(gold_amount) <= 0:
                messages.error(request,
                    "Gold amount must be a valid positive number."
                )
                return render(request, 'trading/create_trade.html', {
                    'offered_pokemon':   offered_pokemon,
                    'user_pokemons':     user_pokemons,
                    'available_pokemons':available_pokemons
                })
            gold_amount = int(gold_amount)

        market_post, _ = MarketPost.objects.get_or_create(
            user=request.user,
            pokemon=offered_pokemon,
            gold=gold_amount,
            requested_pokemon=requested_pokemon,
            defaults={'time_remaining': 1000}
        )

        recipient_user = requested_pokemon.owner if requested_pokemon else market_post.user
        return redirect('Collection.index')

    return render(request, 'trading/create_trade.html', {
        'offered_pokemon':    offered_pokemon,
        'user_pokemons':      user_pokemons,
        'available_pokemons': available_pokemons
    })


@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(
        TradeOffer,
        id=offer_id,
        recipient=request.user
    )

    seller     = offer.offer.user
    buyer      = offer.sender
    listed_poke= offer.offer.pokemon
    trade_poke = offer.pokemon_offered
    gold_amt   = offer.gold or 0

    with transaction.atomic():

        if trade_poke:

            orig_seller = listed_poke.owner
            orig_buyer  = trade_poke.owner

            listed_poke.owner = orig_buyer
            trade_poke.owner  = orig_seller
            listed_poke.save()
            trade_poke.save()


            Transaction.objects.create(
                user=seller,
                transaction_type='trade',
                pokemon=trade_poke,
                received_gold=None,
                traded_with=buyer
            )
            Transaction.objects.create(
                user=buyer,
                transaction_type='trade',
                pokemon=listed_poke,
                received_gold=None,
                traded_with=seller
            )


            if gold_amt:
                seller.profile.gold   += gold_amt
                buyer.profile.gold     = max(0, buyer.profile.gold - gold_amt)
                seller.profile.save()
                buyer.profile.save()

                Transaction.objects.create(
                    user=seller,
                    transaction_type='sale',
                    pokemon=None,
                    received_gold=gold_amt,
                    traded_with=buyer
                )


        else:

            listed_poke.owner = buyer
            listed_poke.save()


            seller.profile.gold   += gold_amt
            buyer.profile.gold     = max(0, buyer.profile.gold - gold_amt)
            seller.profile.save()
            buyer.profile.save()

            Transaction.objects.create(
                user=seller,
                transaction_type='sale',
                pokemon=None,
                received_gold=gold_amt,
                traded_with=buyer
            )


        offer.offer.delete()

    return redirect('trade_offers')


@login_required
def decline_offer(request, offer_id):
    offer = get_object_or_404(
        TradeOffer,
        id=offer_id,
        recipient=request.user
    )
    offer.delete()
    messages.info(request, "Trade offer declined.")
    return redirect('trade_offers')


@login_required
def trade_offers(request):
    incoming = TradeOffer.objects.filter(recipient=request.user)
    return render(request, 'trading/negotiations.html', {
        'trade_offers': incoming
    })


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'trading/transaction_history.html', {
        'transactions': transactions
    })
