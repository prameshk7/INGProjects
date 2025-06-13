from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Todo, TodoUser
from .serializers import TodoSerializer, TodoUserSerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, login


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
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'retrieve']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]  # Allow anonymous for list and register

    def get_queryset(self):
        queryset = Todo.objects.all()  # Allow all todos for GET list
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated:
                return Todo.objects.none()  # Empty for unauthenticated on specific todo
            queryset = queryset.filter(owner=self.request.user)
        completed = self.request.query_params.get('completed', None) # type: ignore
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        queryset = queryset.order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise permissions.AuthenticationFailed("Authentication required. Please register at /api/register/") # type: ignore
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise permissions.AuthenticationFailed("Authentication required. Please register at /api/register/") # type: ignore
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({'error': 'You can only update your own todos.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise permissions.AuthenticationFailed("Authentication required. Please register at /api/register/") # type: ignore
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({'error': 'You can only delete your own todos.'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], serializer_class=TodoUserSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.password = make_password(serializer.validated_data['password'])
            user.save()
            login(request, user)  # Log in the user directly with TodoUser
            return Response({'user': serializer.data, 'message': 'Registration successful, you are now logged in'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)