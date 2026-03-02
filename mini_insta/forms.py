from django import forms
from .models import Post


class CreatePostForm(forms.ModelForm):
    
    files = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False,
    )

    class Meta:
        model = Post
        fields = ["caption"]
