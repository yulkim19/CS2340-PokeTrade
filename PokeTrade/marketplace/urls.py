from django.urls import path

from . import views
from .views import createMarketPost, makeOffer

urlpatterns = [
    path("", views.index, name="index"),
    path('create/', createMarketPost, name='createMarketPost'),
    path('make_offer/<int:post_id>/', makeOffer, name='make_offer'),
    path('delete_offer/', views.deleteOffer, name='delete_offer'),
    path('search/', views.search, name='marketplace.search'),
    path('filter_type/',views.filterType,name='marketplace.filterType'),
    path('filter_rarity/',views.filterRarity,name='marketplace.filterRarity'),
    path("accept/<int:post_id>/", views.accept, name="accept"),
]
