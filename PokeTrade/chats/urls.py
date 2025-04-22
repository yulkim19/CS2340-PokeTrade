from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="chat_home"),
    path("<str:room_name>/<str:username>/", views.room_view, name="chat_room")
]