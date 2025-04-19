from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from supabase_storage import get_file_url, upload_file
from .models import Message  # Assuming Message model is where messages are stored
from django.db.models import Q
from friends.models import Friendship
from notifications.models import Notification
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings
import os
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


@login_required
def dm_view(request, target_user):
    # Get all messages between the current user and the target user
    messages = Message.objects.filter(
        Q(sender=request.user, receiver__username=target_user) | 
        Q(sender__username=target_user, receiver=request.user)
    ).order_by('timestamp')  # Order by the timestamp to show in chronological order

    target_user_obj = get_object_or_404(User, username=target_user)

    unread_notifications_count = 0
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        unread_notifications_count = notifications.filter(is_read=False).count()

    search_term = request.GET.get('friend_search')
    if search_term:
            friends = User.objects.filter(
                Q(username__icontains=search_term)
            )
    elif request.user.is_authenticated:
        friendships = Friendship.objects.filter(user=request.user).select_related('friend')
        friends = [friendship.friend for friendship in friendships]
    else:
        friends = []

    return render(request, 'messaging/dm.html', {
        'current_user': request.user.username,
        'target_user': target_user_obj,
        'messages': messages,
        'unread_notifications_count': unread_notifications_count,
        'friends': friends,
    })



def upload_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_path = f"messages/{request.user.id}/{uploaded_file.name}"

        try:
            upload_response = upload_file(uploaded_file, file_path)
            # If no error, get the public URL
            file_url = get_file_url(file_path)

            return JsonResponse({'file_url': file_url})

        except Exception as e:
            print(f"File upload failed: {e}")
            return JsonResponse({'error': 'Upload failed'}, status=500)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)
        