from django.http import HttpResponse
from django.template import loader
from .forms import PostForm  
from .models import Post
from django.shortcuts import render, redirect

def home(request):
    template = loader.get_template("posts/home.html")
    return HttpResponse(template.render({}, request))

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