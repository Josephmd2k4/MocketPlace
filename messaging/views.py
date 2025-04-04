from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message  # Assuming Message model is where messages are stored
from django.db.models import Q
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

    return render(request, 'messaging/dm.html', {
        'current_user': request.user.username,
        'target_user': target_user_obj,
        'messages': messages,
        'unread_notifications_count': unread_notifications_count,
    })



def upload_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Save the file to the MEDIA_ROOT folder
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Now construct the URL to the file
        file_url = os.path.join(settings.MEDIA_URL, file_name)  # Construct the URL to the saved file

        return JsonResponse({'file_url': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)
