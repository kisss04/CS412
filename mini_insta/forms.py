from django import forms
from .models import Post
from .models import Profile

class CreatePostForm(forms.ModelForm):
    
    files = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False,
    )

    class Meta:
        model = Post
        fields = ["caption"]


class CreateProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'username',
            'display_name',
            'bio_text',
            'profile_image_url'
        ]
