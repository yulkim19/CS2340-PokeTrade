from django.urls import path

from . import views
from .views import generate_pokemon_view

urlpatterns = [
    path("", views.index, name="Collection.index"),
    path("about", views.about, name="Collection.about"),
    path('generate-pokemon/', generate_pokemon_view, name='generate_pokemon'),
]