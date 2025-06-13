from rest_framework import viewsets, permissions
from .models import Todo
from .serializers import TodoSerializer

class TodoViewSet(viewsets.ModelViewSet): # Used viewset for reducing code repetition
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): # Filter todos by the authenticated user
        return Todo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        