from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from .models import Todo, TodoUser
from .serializers import TodoSerializer, TodoUserSerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import make_password

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsOwnerOrReadOnly(permissions.BasePermission): # Custom permission to only allow owners of an object to edit it.
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Todo.objects.none()  # Empty queryset for unauthenticated users
        queryset = Todo.objects.filter(owner=self.request.user) # Filter todos by the authenticated user
        completed = self.request.query_params.get('completed', None) # type: ignore
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        queryset = queryset.order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user: # Check if the user is the owner of the todo item
            return Response({'error': 'You can only update your own todos.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({'error': 'You can only delete your own todos.'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = TodoUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(password=make_password(request.data['password']))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Register a new user

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = TodoUser.objects.filter(username=username).first()
        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400) # Login a user and return a token