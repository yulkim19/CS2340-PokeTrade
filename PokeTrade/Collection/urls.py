from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="Collection.index"),
    path("about", views.about, name="Collection.about"),
]