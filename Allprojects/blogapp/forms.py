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
    
    