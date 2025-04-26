from django.urls import path
from . import views

urlpatterns = [
    path("chats/<str:username>/", views.chat_dashboard, name='chats.chat_dashboard'),
]