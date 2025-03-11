from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from webpush import send_user_notification
from .models import Notification
from django.contrib.contenttypes.models import ContentType
from posts.models import Post
from django.contrib.auth.models import User
from django.core.paginator import Paginator

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
        return JsonResponse({'success': True})
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
        return redirect('notifications:notification_list')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

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
                message=request.POST.get('message'),
                is_read=False  # Initialize attribute
            )
            
            # Prepare payload for WebPush
            payload = {
                'head': f'New Message from {request.user.username}',
                'body': request.POST.get('message'),
                'icon': 'your-icon-url', # TODO ADD USER ICONS
                'url': f'/messages/{notification.id}/'
            }

            # Send WebPush notification
            # send_user_notification(user=recipient, payload=payload, ttl=1000)
            send_dm_notification(request, recipient_id)
            
            return redirect('inbox') and render(request, 'notifications/send-dm/<int:recipient_id>/', {'recipient_id': recipient_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def send_post_notification(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        # Get all users who should be notified 
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
                object_id=post.id,
                is_read=False  # Initialize is_read attribute
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