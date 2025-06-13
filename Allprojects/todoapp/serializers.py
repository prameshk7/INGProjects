from rest_framework import serializers
from .models import Todo

class TodoSerializer(serializers.ModelSerializer): # Using ModelSerializer for automatic field generation
    created_at_display = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%d %H:%M')  # type: ignore
    
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at','created_at_display', 'user']
        
        