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
            requested_pokemon=requested_pokemon,
            defaults={'time_remaining': 1000}
        )

        # Determine correct recipient
        if requested_pokemon:
            recipient_user = requested_pokemon.owner
        else:
            recipient_user = market_post.user

        TradeOffer.objects.create(
            sender=request.user,
            recipient=recipient_user,
            offer=market_post,
            pokemon_offered=offered_pokemon,
            pokemon_requested=requested_pokemon,
            gold=gold_amount or None
        )
        return redirect('Collection.index')

    return render(request, 'trading/create_trade.html', {
        'offered_pokemon':    offered_pokemon,
        'user_pokemons':      user_pokemons,
        'available_pokemons': available_pokemons
    })


@login_required
def accept_offer(request, offer_id):
    # Only the intended recipient can accept
    offer = get_object_or_404(
        TradeOffer,
        id=offer_id,
        recipient=request.user
    )

    sender    = offer.sender
    recipient = offer.recipient
    p_off     = offer.pokemon_offered
    p_req     = offer.pokemon_requested
    gold      = offer.gold or 0

    # Remember the MarketPost so we can delete it later
    market_post = offer.offer

    with transaction.atomic():
        # Straight Pokémon-for-Pokémon
        if p_req:
            # swap owners
            owner_a = p_off.owner  # should be sender
            owner_b = p_req.owner  # should be recipient

            p_off.owner = owner_b
            p_req.owner = owner_a
            p_off.save()
            p_req.save()

            # record transactions
            Transaction.objects.create(
                user=sender,
                transaction_type='trade',
                pokemon=p_req,
                received_gold=None,
                traded_with=recipient
            )
            Transaction.objects.create(
                user=recipient,
                transaction_type='trade',
                pokemon=p_off,
                received_gold=None,
                traded_with=sender
            )

        # Pokémon-for-Gold sale
        else:
            # transfer Pokémon to buyer
            p_off.owner = recipient
            p_off.save()

            # adjust gold balances (assuming profile.gold exists)
            sender.profile.gold   += gold
            recipient.profile.gold = max(0, recipient.profile.gold - gold)
            sender.profile.save()
            recipient.profile.save()

            Transaction.objects.create(
                user=sender,
                transaction_type='sale',
                pokemon=None,
                received_gold=gold,
                traded_with=recipient
            )

        # delete the marketplace post (cascades to TradeOffer if needed)
        market_post.delete()

    # Redirect to incoming offers
    return redirect('trade_offers')


@login_required
def decline_offer(request, offer_id):
    # Only the recipient may decline
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
    # Show only offers meant for the current user
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
