from django.shortcuts import render

# Create your views here.
def home_view(request):
    return render(request, "chat_home.html")

def room_view(request, room_name, username):
    return render(request, "chat_room.html")