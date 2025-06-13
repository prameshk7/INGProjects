from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Todo, TodoUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def unique_username_validator(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError("This username is already taken.")

class TodoUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) 
    username = serializers.CharField(validators=[unique_username_validator])

    class Meta:
        model = TodoUser
        fields = ['id', 'username', 'email', 'password']  # Exclude user from fields
        extra_kwargs = {'user': {'read_only': True}}  # Ensure user is read-only

    def create(self, validated_data):
        # Extract password and create User instance
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )
        todo_user = TodoUser.objects.create(user=user, username=validated_data['username'], email=validated_data['email'])
        return todo_user
 
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise ValidationError("Invalid username or password")
        return data   

class TodoSerializer(serializers.ModelSerializer):
    owner = TodoUserSerializer(read_only=True)
    created_at_display = serializers.SerializerMethodField()

    def get_created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else None

    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'created_at_display', 'owner']
        
        