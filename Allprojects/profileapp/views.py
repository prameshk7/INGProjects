from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import ProfileForm,UserForm, PasswordResetRequestForm, PasswordResetConfirmForm
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Profile, OTP
import random
import string
from datetime import timedelta
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Redirecting to login...')
            return redirect('profileapp:login')
    else:
        form = UserForm()
    return render(request, 'profileapp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful. Redirecting to profile...')
            return redirect('profileapp:profile')
    else:
        form = AuthenticationForm()
    return render(request, 'profileapp/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('profileapp:login')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('profileapp:login')
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'profileapp/profile.html', {'form': form})

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate OTP
                otp = ''.join(random.choices(string.digits, k=6))
                OTP.objects.filter(user=user).delete()  # Clear old OTPs
                otp_obj = OTP.objects.create(user=user, otp=otp)
                otp_obj.save()
                # Send OTP via email
                subject = 'Password Reset OTP'
                message = f'Your OTP for password reset is: {otp}\nThis OTP is valid for 10 minutes.'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, f'OTP has been sent to {email}.')
                return redirect('profileapp:password_reset_confirm')
            except User.DoesNotExist:
                messages.error(request, 'No user exists with this email address.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'profileapp/password_reset_request.html', {'form': form})

def password_reset_confirm(request):
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'profileapp/password_reset_confirm.html', {'form': form})
            try:
                user = User.objects.get(email=email)
                otp_obj = OTP.objects.filter(user=user, otp=otp, is_used=False).first()
                if not otp_obj:
                    messages.error(request, 'Invalid or expired OTP.')
                    return render(request, 'profileapp/password_reset_confirm.html', {'form': form})
                if timezone.now() > otp_obj.created_at + timedelta(minutes=10):
                    messages.error(request, 'OTP has expired.')
                    otp_obj.delete()
                    return render(request, 'profileapp/password_reset_confirm.html', {'form': form})
                user.set_password(new_password)
                user.save()
                otp_obj.is_used = True
                otp_obj.save()
                messages.success(request, 'Password reset successful.')
                return redirect('profileapp:login')
            except User.DoesNotExist:
                messages.error(request, 'No user exists with this email address.')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'profileapp/password_reset_confirm.html', {'form': form})