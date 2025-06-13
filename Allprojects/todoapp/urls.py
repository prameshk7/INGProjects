
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet

router = DefaultRouter() # Create a router and register our viewset with it
router.register(r'todos', TodoViewSet, basename='todos')

urlpatterns = [
    path('', include(router.urls)), # Include the router's URLs
]