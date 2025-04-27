from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message


@login_required
def chat_dashboard(request, username=None):
    if username:
        usernames = sorted([request.user.username, username])
        room_name = f"{usernames[0]}_{usernames[1]}"

        # Fetch chat history between the two users
        messages = Message.objects.filter(
            sender__username__in=[request.user.username, username],
            receiver__username__in=[request.user.username, username]
        ).order_by('timestamp')

        if request.method == "POST":
            message_text = request.POST.get('message')
            if message_text:
                receiver = User.objects.get(username=username)
                new_message = Message.objects.create(
                    sender = request.user,
                    receiver = receiver,
                    message = message_text
                )
                return redirect('chats.chat_dashboard', username=username)

        context = {
            'room_name': room_name,
            'recipient': username,
            'sender': request.user.username,
            'messages': messages,
        }
    else:
        users = User.objects.exclude(username=request.user.username)
        context = {
            'users': users,
            'room_name': None
        }

    return render(request, 'chats/chat_home.html', context)

