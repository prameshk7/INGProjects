from rest_framework import serializers
from .models import Todo, TodoUser

class TodoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoUser
        fields = ['id', 'username', 'email']

class TodoSerializer(serializers.ModelSerializer):
    owner = TodoUserSerializer(read_only=True)
    created_at_display = serializers.SerializerMethodField()

    def get_created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else None

    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'created_at_display', 'owner']