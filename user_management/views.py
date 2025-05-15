from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm,
    UserProfileForm, 
    UserUpdateForm
)
from .models import UserProfile, UserActivity

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Use get_or_create to prevent IntegrityError
            UserProfile.objects.get_or_create(user=user)
            
            # Log the user in directly
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('election_list')  # Changed from 'dashboard' to 'election_list'
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'user_management/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Record activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='LOGIN',
                    description='User logged in',
                    ip_address=get_client_ip(request)
                )
                
                messages.success(request, f'Welcome back, {username}!')
                return redirect('election_list')  # Redirect to voting homepage
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user_management/login.html', {'form': form})

def user_logout(request):
    if request.user.is_authenticated:
        # Record activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='LOGOUT',
            description='User logged out',
            ip_address=get_client_ip(request)
        )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile(request):
    # Use get_or_create to safely get or create a profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Record activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='PROFILE_UPDATE',
                description='User updated profile information',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    return render(request, 'user_management/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def activity_log(request):
    activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'user_management/activity_log.html', {'activities': activities})

# Helper functions
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
