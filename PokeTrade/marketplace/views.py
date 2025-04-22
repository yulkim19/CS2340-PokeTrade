from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import MarketPost
from .utils import createMarketPost, createTradeOffer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from  Collection.models import Pokemon
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


def makeOffer(request):
    if request.method == "POST":
        seller_username = request.POST.get('seller_username')
        seller_pokemon = request.POST.get('seller_pokemon')

        seller = User.objects.get(username=seller_username)
        seller_pokemon = Pokemon.objects.get(name=seller_pokemon, owner=seller)
        offer = MarketPost.objects.get(user=seller, pokemon=seller_pokemon)
        pokemon_name = request.POST.get('pokemon_name')
        gold = request.POST.get('gold')
        if pokemon_name is not None or pokemon_name != '':
            pokemon = Pokemon.objects.get(name=pokemon_name, owner=request.user)
        else:
            pokemon = None
        createTradeOffer(offer, request.user, pokemon, gold)
    return redirect('marketplace.index')


