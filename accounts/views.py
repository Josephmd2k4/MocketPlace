from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm  # Import the custom form
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserChangeForm, CustomPasswordChangeForm
from .forms import ProfileForm
from .models import Profile
from notifications.models import Notification

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user instance but don't save yet
            user.first_name = form.cleaned_data.get('first_name')  # Assign first name
            user.last_name = form.cleaned_data.get('last_name')  # Assign last name
            user.save()  # Now save the user with first & last name
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:login')
        else:
            if form.cleaned_data.get('username') and User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'A user with that username already exists.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

from django.shortcuts import get_object_or_404

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    unread_notifications_count = 0
    if request.user.is_authenticated and request.user == user:
        notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
        unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'accounts/profile.html', {
        'user': user,
        'unread_notifications_count': unread_notifications_count
    })



@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('accounts:profile', username=username)

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})



@login_required
def settings_view(request, username):
    if request.user.username != username:
        return redirect('accounts:profile', username=username)

    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been updated successfully.")
            return redirect('accounts:settings', username=username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/settings.html', {'form': form})


def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    unread_notifications_count = 0
    if request.user.is_authenticated and request.user == user:
        notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
        unread_notifications_count = notifications.filter(is_read=False).count()
    
    return render(request, 'accounts/profile.html', {
        'user': user,
        'unread_notifications_count': unread_notifications_count
    })
@login_required
def redirect_to_own_profile(request):
    return redirect('accounts:profile', username=request.user.username)

