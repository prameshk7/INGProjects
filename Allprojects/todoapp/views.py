from rest_framework import viewsets, permissions
from .models import Todo
from .serializers import TodoSerializer
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user)
        completed = self.request.GET.get('completed', None)  # Filtering by completed status
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        queryset = queryset.order_by('-created_at')  # Ordering by created_at
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)