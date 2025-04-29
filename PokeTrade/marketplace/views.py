

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q

from Collection.models import Pokemon
from .models import MarketPost
from trading.models import TradeOffer  # still needed for makeOffer

@login_required
def index(request):
    your_posts  = MarketPost.objects.filter(user=request.user)
    other_posts = MarketPost.objects.exclude(user=request.user)
    return render(request, "marketplace/marketplaceview.html", {
        'yourPosts':  your_posts,
        'otherPosts': other_posts
    })

@login_required
def createMarketPost(request):
    if request.method == "POST":

        offered_name = request.POST.get('pokemon_name')
        offered_pokemon = get_object_or_404(
            Pokemon,
            name=offered_name,
            owner=request.user
        )


        requested_pokemon = None
        req_name = request.POST.get('requested_pokemon_name')
        if req_name:
            requested_pokemon = get_object_or_404(
                Pokemon,
                name=req_name,
                owner=request.user
            )


        gold = None
        gold_str = request.POST.get('gold')
        if gold_str:
            if not gold_str.isdigit() or int(gold_str) <= 0:
                messages.error(request, 'Requested gold must be a positive integer.')
                return redirect('index')
            gold = int(gold_str)


        if requested_pokemon is None and gold is None:
            messages.error(request, 'You must request either gold or a Pokémon.')
            return redirect('index')


        # 5) Create the listing
        MarketPost.objects.create(
            user=request.user,
            pokemon=offered_pokemon,
            requested_pokemon=requested_pokemon,
            gold=gold,
            time_remaining=120
        )
        messages.success(request, "Your Pokémon is now listed on the marketplace!")
    return redirect('index')

def filterType(request):
    t = request.GET.get('type', '')
    your_posts  = MarketPost.objects.filter(
        Q(pokemon__primary_type=t) | Q(pokemon__secondary_type=t),
        user=request.user
    )
    other_posts = MarketPost.objects.filter(
        Q(pokemon__primary_type=t) | Q(pokemon__secondary_type=t)
    ).exclude(user=request.user)
    return render(request, "marketplace/searchview.html", {
        'yourPosts':  your_posts,
        'otherPosts': other_posts
    })

def filterRarity(request):
    r = request.GET.get('rarity', 0)
    your_posts  = MarketPost.objects.filter(
        pokemon__rarity__gte=r,
        user=request.user
    )
    other_posts = MarketPost.objects.filter(
        pokemon__rarity__gte=r
    ).exclude(user=request.user)
    return render(request, "marketplace/searchview.html", {
        'yourPosts':  your_posts,
        'otherPosts': other_posts
    })

@login_required
def search(request):
    q = request.GET.get('search', '')
    your_posts  = MarketPost.objects.filter(
        pokemon__name__istartswith=q,
        user=request.user
    )
    other_posts = MarketPost.objects.filter(
        pokemon__name__istartswith=q
    ).exclude(user=request.user)
    return render(request, "marketplace/searchview.html", {
        'yourPosts':  your_posts,
        'otherPosts': other_posts
    })

@login_required
def makeOffer(request, post_id):
    market_post = get_object_or_404(MarketPost, id=post_id)
    if request.method == "POST":
        offered_name = request.POST.get('pokemon_name')
        gold_str     = request.POST.get('gold')

        gold = None
        if gold_str:
            if not gold_str.isdigit() or int(gold_str) <= 0:
                messages.error(request, 'Gold amount must be a positive integer.')
                return redirect('make_offer', post_id=post_id)
            gold = int(gold_str)

        offered_pokemon = None
        if offered_name:
            offered_pokemon = get_object_or_404(
                Pokemon,
                name=offered_name,
                owner=request.user
            )

        if not offered_pokemon and gold is None:
            messages.error(request, 'You must offer either a Pokémon or some gold.')
            return redirect('make_offer', post_id=post_id)

        TradeOffer.objects.create(
            sender=request.user,
            recipient=market_post.user,
            offer=market_post,
            pokemon_offered=offered_pokemon,
            pokemon_requested=market_post.pokemon,
            gold=gold
        )
        messages.success(request, 'Your trade offer has been submitted!')
    return redirect('index')

@require_POST
@login_required
def deleteOffer(request):
    post_id = request.POST.get("post_id")
    post = get_object_or_404(
        MarketPost,
        id=post_id,
        user=request.user
    )
    post.delete()
    messages.success(request, 'Your marketplace listing has been removed.')
    return redirect('index')

@require_POST
@login_required
def accept(request, post_id):
    post   = get_object_or_404(MarketPost, id=post_id)
    buyer  = request.user
    seller = post.user


    if buyer == seller:
        return HttpResponseForbidden("You cannot accept your own listing.")


    wants_pokemon = post.requested_pokemon is not None
    wants_gold    = post.gold is not None and post.gold > 0


    if not (wants_pokemon or wants_gold):
        messages.error(request, "Invalid marketplace listing.")
        return redirect('index')


    if wants_pokemon:
        requested = post.requested_pokemon
        if requested.owner != buyer:
            messages.error(request, "You don’t own the requested Pokémon.")
            return redirect('index')
        requested.owner = seller
        requested.save()


    if wants_gold:
        if buyer.profile.gold < post.gold:
            messages.error(request, "You don’t have enough gold.")
            return redirect('index')
        buyer.profile.gold  -= post.gold
        seller.profile.gold += post.gold
        buyer.profile.save()
        seller.profile.save()


    offered = post.pokemon
    offered.owner = buyer
    offered.save()


    post.delete()

    messages.success(request, "Trade completed successfully!")
    return redirect('index')
