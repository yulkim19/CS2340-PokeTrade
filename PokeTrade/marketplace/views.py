from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import MarketPost

# Create your views here.
def index(request):
    yourPosts = MarketPost.objects.filter(user=request.user)
    otherPosts = MarketPost.objects.exclude(user=request.user)
    context = {
        'yourPosts': yourPosts,
        'otherPosts': otherPosts
    }
    return HttpResponse("HI")