from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

app_name = 'profileapp'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password_reset/', PasswordResetView.as_view(template_name='profileapp/password_reset.html', email_template_name='profileapp/password_reset_email.html', success_url=reverse_lazy('profileapp:password_reset_done')), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='profileapp/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='profileapp/password_reset_confirm.html', success_url=reverse_lazy('profileapp:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='profileapp/password_reset_complete.html'), name='password_reset_complete'),
]