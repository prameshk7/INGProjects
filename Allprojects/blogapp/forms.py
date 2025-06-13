from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

    def clean(self):                #this method prevent whitespaces
        input_data = super().clean()
        title = input_data.get('title')
        content = input_data.get('content')
        if not title or not title.strip():
            raise forms.ValidationError("Title cannot be empty.")
        if not content or not content.strip():
            raise forms.ValidationError("Content cannot be empty.")
        return input_data
 
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Add email field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # Basic validation for email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email   
    