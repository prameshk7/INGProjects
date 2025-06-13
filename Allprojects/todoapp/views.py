from rest_framework import viewsets, permissions
from .models import Todo
from .serializers import TodoSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]  # Allow anonymous GET

    def get_queryset(self):
        queryset = Todo.objects.all()  # Allow all for GET list
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            queryset = queryset.filter(owner=self.request.user)
        completed = self.request.GET.get('completed', None)
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        queryset = queryset.order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed("Authentication required to create a todo.")
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication required to update a todo.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication required to delete a todo.")
        return super().destroy(request, *args, **kwargs)
    
    