from django.http import HttpResponse
from django.template import loader
from .forms import PostForm  
from .models import Post
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from notifications.views import mark_notification_read, mark_all_read, send_dm_notification, send_post_notification

def home(request):
    template = loader.get_template("posts/home.html")
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all().order_by('created_at')
    return render(request, 'posts/home.html', {'posts': posts})

@login_required
def createPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            send_post_notification(request)
            return redirect('/')  
    else:
        form = PostForm()

    return render(request, 'posts/createPost.html', {'form': form})

