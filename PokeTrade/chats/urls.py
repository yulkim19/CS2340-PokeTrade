from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_dashboard, name='chats.chat_dashboard'),
    path("<str:username>/", views.chat_dashboard, name='chats.chat_dashboard_username'),
]