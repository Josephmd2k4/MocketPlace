from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message  # Assuming Message model is where messages are stored
from django.db.models import Q

@login_required
def dm_view(request, target_user):
    # Get all messages between the current user and the target user
    messages = Message.objects.filter(
        Q(sender=request.user, receiver__username=target_user) | 
        Q(sender__username=target_user, receiver=request.user)
    ).order_by('timestamp')  # Order by the timestamp to show in chronological order

    return render(request, 'messaging/dm.html', {
        'current_user': request.user.username,
        'target_user': target_user,
        'messages': messages,
    })


