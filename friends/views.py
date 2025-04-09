from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import FriendRequest, Friendship
from notifications.models import Notification

User = get_user_model()

def send_friend_request(request, receiver_id):
    if request.method == "POST":
        receiver = get_object_or_404(User, id=receiver_id)

        # Prevent duplicate requests
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
            return JsonResponse({"message": "Friend request already sent."}, status=400)
        
        if Friendship.objects.filter(user=request.user, friend=receiver).exists():
            response_message = f"You and {receiver} are already friends!" 
            return JsonResponse({"message": response_message}, status=400)

        # Create the friend request
        friend_request = FriendRequest.objects.create(sender=request.user, receiver=receiver)

        # Send notification to the receiver
        notification = Notification.objects.create(
            recipient=receiver,
            sender=request.user,
            notification_type='FRIEND_REQUEST',
            title=f"You have a new friend request from {request.user.username}",
            message_text=f"{request.user.username} has sent you a friend request. Click to respond.",
            friend_request_id=friend_request.id
        )

        return JsonResponse({"message": "Friend request sent!"})

    return JsonResponse({"error": "Invalid request method."}, status=400)

def accept_friend_request(request, request_id):
    if request.method == "POST":
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

        # Accept the friend request
        friend_request.accept()

        # Create a Friendship record for both users
        Friendship.objects.create(user=friend_request.sender, friend=friend_request.receiver)
        Friendship.objects.create(user=friend_request.receiver, friend=friend_request.sender)

        # Send notification to the sender
        notification = Notification.objects.create(
            recipient=friend_request.sender,
            sender=request.user,
            notification_type='FRIEND_REQUEST_ACCEPTED',
            title=f"{request.user.username} accepted your friend request.",
            message_text=f"{request.user.username} has accepted your friend request. You are now friends.",
            friend_request_id=friend_request.id
        )

        notification_to_delete = Notification.objects.get(friend_request_id=friend_request.id, recipient=request.user)
        notification_to_delete.delete()

        return redirect(reverse('notifications:notifications_list'))

    return JsonResponse({"error": "Invalid request method."}, status=400)

def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if friend_request.receiver != request.user:
        return JsonResponse({'message': 'Not authorized!'}, status=403)

    friend_request.status = 'rejected'
    friend_request.save()

    notification_to_delete = Notification.objects.get(friend_request_id=friend_request.id, recipient=request.user)
    notification_to_delete.delete()
    
    return redirect(reverse('notifications:notifications_list'))

def list_friends(request):
    friends = Friendship.objects.filter(user=request.user).values_list('friend__username', flat=True)
    return JsonResponse({'friends': list(friends)})
