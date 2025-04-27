from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import MarketPost
from .utils import createMarketPost, createTradeOffer
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from Collection.models import Pokemon
from trading.models import Transaction


# Create your views here.

@login_required
def index(request):
    yourPosts = MarketPost.objects.filter(user=request.user)
    otherPosts = MarketPost.objects.exclude(user=request.user)
    context = {
        'yourPosts': yourPosts,
        'otherPosts': otherPosts
    }
    return render(request, "marketplace/marketplaceview.html", context)


@login_required
def createMarketPost(request):
    if request.method == "POST":
        pokemon_name = request.POST.get('pokemon_name')
        pokemon = Pokemon.objects.get(name=pokemon_name, owner=request.user)
        createMarketPost(request.user, pokemon)
    return redirect('marketplace.index')


def makeOffer(request, post_id):
    offer = get_object_or_404(MarketPost, id=post_id)
    if request.method == "POST":
        seller_username = offer.user.username
        seller_pokemon = offer.pokemon.name

        seller = get_object_or_404(User, username=seller_username)
        seller_pokemon = get_object_or_404(Pokemon, name=seller_pokemon, owner=seller)
        offer = get_object_or_404(MarketPost, user=seller, pokemon=seller_pokemon)
        pokemon_name = request.POST.get('pokemon_name')
        gold = request.POST.get('gold')


        if gold and (not gold.isdigit() or int(gold) <= 0):
            messages.error(request, 'Gold amount must be a valid positive number.')
            return redirect('make_offer', post_id=offer.id)

        gold = int(gold) if gold else None

        pokemon = None
        if pokemon_name:
            pokemon = get_object_or_404(Pokemon, name=pokemon_name, owner=request.user)

        if not pokemon and not gold:
            messages.error(request, 'You must offer either a Pokemon or an amount of gold.')
            return redirect('make_offer', post_id=offer.id)

        createTradeOffer(offer, request.user, pokemon, gold)
        return redirect('index')
    return redirect('index')

@require_POST
@login_required
def deleteOffer(request):
    post_id = request.POST.get("post_id")
    post = get_object_or_404(MarketPost, id=post_id, user=request.user)
    post.delete()
    return redirect('index')
