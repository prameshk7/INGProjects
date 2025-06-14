from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

app_name = 'profileapp'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]