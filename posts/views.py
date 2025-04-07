from .forms import PostForm  
from .models import Post, Comment
from friends.models import Friendship
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from notifications.views import mark_notification_read, mark_all_read, send_dm_notification, send_post_notification, send_comment_notification
from notifications.models import Notification
from .models import Media
from accounts.models import User
from django.urls import reverse
from django.db.models import Q


def home(request):
    query = request.GET.get('q')
    open_modal = request.GET.get('open_modal')
    success = request.GET.get('success')

    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |  
            Q(user__username__icontains=query)  
        )

    else:
        posts = Post.objects.all().prefetch_related("comments").order_by('-created_at')

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
        

    return render(request, 'posts/home.html', {'posts': posts, 'open_modal': open_modal, 'unread_notifications_count': unread_notifications_count,
        'success': success,'friends': friends})

@login_required
def createPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        files = request.FILES.getlist('files')  # Fetch multiple files

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  
            post.save()

            # Save multiple media files
            for file in files:
                Media.objects.create(post=post, file=file)

            return redirect('/')  # Redirect to homepage or post detail
    else:
        form = PostForm()

    return render(request, 'posts/createPost.html', {'form': form})

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = get_object_or_404(Post, id=post_id)

        # Create the comment
        comment = Comment.objects.create(post=post, user=request.user, content=content)

        # Trigger the new comment notification
        send_comment_notification(request.user, post, comment.id)

        # Redirect back to the post page (with a modal or open section)
        return redirect(f"{reverse('home')}?open_modal={post_id}")

