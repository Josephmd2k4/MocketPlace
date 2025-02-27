from .forms import PostForm  
from .models import Post, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

def home(request):
    query = request.GET.get('q')
    open_modal = request.GET.get('open_modal') 
    if query:
        posts = Post.objects.filter(title__icontains=query).prefetch_related("comments").order_by('-created_at')
    else:
        posts = Post.objects.all().prefetch_related("comments").order_by('-created_at')

    return render(request, 'posts/home.html', {'posts': posts, 'open_modal': open_modal})

@login_required
def createPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  
            return redirect('/')  
    else:
        form = PostForm()

    return render(request, 'posts/createPost.html', {'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)

    return redirect(f"/?open_modal={post.id}")

