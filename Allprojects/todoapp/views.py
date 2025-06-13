from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Todo, TodoUser
from .serializers import LoginSerializer, TodoSerializer, TodoUserSerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.models import User
from django.utils.functional import SimpleLazyObject

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user._wrapped if isinstance(request.user, SimpleLazyObject) and hasattr(request.user, '_wrapped') else request.user
        print(f"Permission Check - Request user: {user}, Type: {type(user)}, Owner user: {obj.owner.user}, Type: {type(obj.owner.user)}")
        if request.method in permissions.SAFE_METHODS:
            return True
        return user and obj.owner.user == user

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
            try:
                queryset = queryset.filter(owner__user=self.request.user)
            except ValueError as e:
                return Todo.objects.none()  # Return empty queryset on error
        completed = self.request.query_params.get('completed', None)  # type: ignore
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        queryset = queryset.order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise permissions.AuthenticationFailed("Authentication required. Please register at /api/register/") # type: ignore
        todo_user, created = TodoUser.objects.get_or_create(user=self.request.user)
        serializer.save(owner=todo_user)
    
    def update(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise permissions.AuthenticationFailed("Authentication required. Please register at /api/register/")  # type: ignore
        instance = self.get_object()
        # Resolve the lazy user object
        user = request.user._wrapped if isinstance(request.user, SimpleLazyObject) and hasattr(request.user, '_wrapped') else request.user
        print(f"Update Check - Request user: {user}, Type: {type(user)}, Owner user: {instance.owner.user}, Type: {type(instance.owner.user)}")
        if instance.owner.user != user:
            return Response({'error': 'You can only update your own todos.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise permissions.AuthenticationFailed("Authentication required. Please register at /api/register/")  # type: ignore
        instance = self.get_object()
        # Resolve the lazy user object
        user = request.user._wrapped if isinstance(request.user, SimpleLazyObject) and hasattr(request.user, '_wrapped') else request.user
        print(f"Delete Check - Request user: {user}, Type: {type(user)}, Owner user: {instance.owner.user}, Type: {type(instance.owner.user)}")
        if instance.owner.user != user:
            return Response({'error': 'You can only delete your own todos.'}, status=403)
        return super().destroy(request, *args, **kwargs)


    @action(detail=False, methods=['post'], serializer_class=TodoUserSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            todo_user = serializer.save()  # Save the new TodoUser instance
            user = todo_user.user  # Get the linked User instance
            login(request, user)
            # Ensure session is saved
            request.session.save()
            return Response({'user': serializer.data, 'message': 'Registration successful, you are now logged in'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'post'], serializer_class=LoginSerializer)
    def login(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = authenticate(request, username=serializer.validated_data['username'], password=serializer.validated_data['password'])
                if user is not None:
                    login(request, user)
                    request.session.save()
                    return Response({'message': 'Login successful, you are now logged in'}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)  # Render the form for GET request