from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='list'),
    path('post/<int:id>/', views.post_detail, name='detail'),
    path('post/new/', views.post_create, name='create'),
    path('post/<int:id>/edit/', views.post_update, name='update'),
    path('post/<int:id>/delete/', views.post_delete, name='delete'),
    path('login/', views.user_login, name='login'), 
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'), 
]

