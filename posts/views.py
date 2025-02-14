from django.http import HttpResponse
from django.template import loader
from .forms import PostForm  
from .models import Post
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    template = loader.get_template("posts/home.html")
    posts = Post.objects.all().order_by('created_at')
    return render(request, 'posts/home.html', {'posts': posts})
    return HttpResponse(template.render({}, request))

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

def postDetail(request):
    pass

def myPosts(request):
    pass