# views.py
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message

@login_required
def chat_dashboard(request, username=None):
    chatted_users = User.objects.filter(
        Q(sent_messages__receiver=request.user) |  # Messages where the current user is the receiver
        Q(received_messages__sender=request.user)  # Messages where the current user is the sender
    ).exclude(username=request.user.username).distinct()  # Exclude the current user from the list

    if username:
        # Ensure that the recipient user exists
        recipient = User.objects.filter(username=username).first()

        if not recipient:
            # If the recipient doesn't exist, redirect to the user list
            return redirect('chats.chat_dashboard')

        # Get sorted usernames to create a unique room name
        usernames = sorted([request.user.username, recipient.username])
        room_name = f"{usernames[0]}_{usernames[1]}"

        # Fetch messages between the two users
        messages = Message.objects.filter(
            sender__username__in=[request.user.username, recipient.username],
            receiver__username__in=[request.user.username, recipient.username]
        ).order_by('timestamp')

        # Handle sending a new message
        if request.method == "POST":
            message_text = request.POST.get('message')
            if message_text:
                # Create the new message
                Message.objects.create(
                    sender=request.user,
                    receiver=recipient,
                    message=message_text
                )

                # After sending a message, return to the chat page with the updated user list
                return redirect('chats.chat_dashboard_username', username=username)

        context = {
            'room_name': room_name,
            'users': chatted_users,
            'recipient': recipient.username,
            'sender': request.user.username,
            'messages': messages,
            'show_messages': True,
        }


    else:
        # No active chat, so the room name will be None
        context = {
            'users': chatted_users,
            'room_name': None,  # No active chat
            'show_messages': False,  # No messages to show in this case
        }

    return render(request, 'chats/chat_home.html', context)
