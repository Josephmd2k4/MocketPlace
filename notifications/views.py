from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from webpush import send_user_notification
from .models import Notification
from django.contrib.contenttypes.models import ContentType
from posts.models import Post
from django.contrib.auth.models import User

@login_required
def send_dm_notification(request, recipient_id):
    if request.method == 'POST':
        try:
            recipient = User.objects.get(id=recipient_id)
            
            # Create notification record
            notification = Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type='DM',
                title=request.POST.get('subject'),
                message=request.POST.get('message')
            )
            
            # Prepare payload for WebPush
            payload = {
                'head': f'New Message from {request.user.username}',
                'body': request.POST.get('message'),
                'icon': 'your-icon-url',
                'url': f'/messages/{notification.id}/'
            }

            # Send WebPush notification
            send_user_notification(user=recipient, payload=payload, ttl=1000)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def send_post_notification(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        # Get all users who should be notified (you can customize this based on your requirements)
        users_to_notify = User.objects.exclude(id=request.user.id)
        
        for user in users_to_notify:
            # Create notification record
            notification = Notification.objects.create(
                recipient=user,
                sender=request.user,
                notification_type='POST',
                title=f'New Post: {post.title[:50]}',
                message=f'{request.user.username} has created a new post',
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id
            )
            
            # Prepare payload for WebPush
            payload = {
                'head': 'New Post',
                'body': f'{request.user.username} has created a new post: {post.title[:50]}',
                'icon': 'your-icon-url',
                'url': f'/posts/{post.id}/'
            }
            
            # Send WebPush notification
            send_user_notification(user=user, payload=payload, ttl=1000)
            
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })