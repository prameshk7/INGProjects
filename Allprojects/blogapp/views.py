from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm, RegisterForm
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list')  # Redirect to list of posts
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html', {})

def user_logout(request):
    logout(request)
    return redirect('list')

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create new user
            login(request, user)  # Auto-login after registration
            messages.success(request, 'Registration successful!')
            return redirect('list')  # Redirect to list of posts
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def post_list(request):
    posts = Post.objects.all().order_by('-published_date')
    return render(request, 'list.html', {'posts': posts})

def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    return render(request, 'detail.html', {'post': post})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)     # Set the author before saving
            post.author = request.user
            post.save()
            return redirect('detail', id=post.id)
    else:
        form = PostForm()
    return render(request, 'form.html', {'form': form, 'action': 'Create Post'})

@login_required
def post_update(request, id):    # Method to update the post
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:       # Block users who are not the authors
        return HttpResponseForbidden("Sorry, you can't edit this post.")
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detail', id=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'form.html', {'form': form, 'action': 'Update Post'})

@login_required
def post_delete(request, id):  # Method to delete the post
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:     # Only authors can delete the post
        return HttpResponseForbidden("Sorry, you can't delete this post.")
    if request.method == 'POST':
        post.delete()
        return redirect('list')
    return render(request, 'delete.html', {'post': post})

