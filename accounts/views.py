from django.shortcuts import render, redirect
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
                try:
                    user.profile  
                except Profile.DoesNotExist:
                    messages.error(request, 'User does not exist.')
                    return render(request, 'accounts/login.html', {'form': form})
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

@login_required
def profile_view(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'accounts/profile.html', {'user': request.user, 'unread_notifications_count': unread_notifications_count})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)  # Ensure profile exists

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES,  instance=request.user.profile, user=request.user)
        if form.is_valid():
            # Save user fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()  # Save User model changes

            # Save Profile fields
            profile = form.save(commit=False)  # Don't save to DB yet, we need to handle profile_image
            if form.cleaned_data.get('profile_image'):
                profile.profile_image = form.cleaned_data['profile_image']
            profile.save()  # Save Profile model changes
            
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')  # Redirect to profile page
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def settings_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, "Your password has been updated successfully.")
            return redirect('accounts:settings')  # Stay on the settings page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/settings.html', {'form': form})