from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from webpush import send_user_notification
from .models import Notification
from django.contrib.contenttypes.models import ContentType
from posts.models import Post
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from messaging.models import Message

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return redirect(request.META.get('HTTP_REFERER', 'notifications:list'))  
    except Notification.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'Notification not found'},
            status=404
        )
    
@login_required
@require_POST
def mark_all_read(request):
    try:
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        notifications.update(is_read=True)
        return redirect('notifications:notifications_list')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


from django.db import transaction

def send_dm_notification(sender_username, receiver_username, message_id):
    try:
        with transaction.atomic():  # Ensure atomic transaction
            sender = User.objects.get(username=sender_username)
            receiver = User.objects.get(username=receiver_username)

            notification = Notification.objects.create(
                recipient=receiver,
                sender=sender,  
                notification_type='DM',
                title=f'New Message from {sender_username}',
                object_id=message_id,
                is_read=False  
            )

            # Prepare payload for WebPush
            payload = {
                'head': 'New DM',
                'body': f'{sender.username} has sent you a message',
                'icon': 'your-icon-url',
            }

            # Send WebPush notification
            send_user_notification(user=receiver, payload=payload, ttl=1000)

            return JsonResponse({'status': 'success'})

    except Exception as e:
        print(f"Error creating notification: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})


def send_post_notification(user, post_id):
    try:
        post = Post.objects.get(id=post_id)
        # Get all users who should be notified, excluding the current user
        users_to_notify = User.objects.exclude(id=user.id)
        
        for recipient in users_to_notify:
            # Create notification record
            notification = Notification.objects.create(
                recipient=recipient,
                sender=user,  # The sender is now the user who created the post
                notification_type='POST',
                title=f'New Post: {post.title[:50]}',
                message_text=f'{user.username} has created a new post',
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id,
                is_read=False  # Initialize is_read attribute
            )
            
            # Prepare payload for WebPush
            payload = {
                'head': 'New Post',
                'body': f'{user.username} has created a new post: {post.title[:50]}',
                'icon': 'your-icon-url',
                'url': f'/posts/{post.id}/'
            }
            
            # Send WebPush notification
            send_user_notification(user=recipient, payload=payload, ttl=1000)
            
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def notifications_list(request):
    try:
        # Get notifications for the logged-in user
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        unread_count = notifications.filter(is_read=False).count()

        # Pagination
        paginator = Paginator(notifications, 10)  # Show 10 notifications per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Create the context dictionary
        context = {
            'notifications': page_obj,
            'unread_notifications_count': unread_count,
            'user': request.user,
            'page_title': 'My Notifications',
            'is_admin': request.user.is_staff,
            'notification_types': {
                'DM': 'Direct Message',
                'OFFER': 'New Offer',
                'PRICE': 'Price Alert'
            }
        }
        return render(request, 'notifications/notification_list.html', context)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def buy_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user.is_authenticated:
        # Create a notification for the post owner
        message = f"{request.user.username} is interested in your  {post.title}"
        
        # Create the notification
        Notification.objects.create(
            recipient=post.user,  
            title=message,
            sender=request.user
        )
        
        # You can redirect or render a page after processing the action
        return redirect('/?success=true') 
    else:
        return redirect('login')  # Redirect to the login page