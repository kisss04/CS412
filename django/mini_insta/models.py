from django.db import models
from django.urls import reverse
# Create your models here.
from django.db import models

class Profile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    profile_image_url = models.URLField()
    bio_text = models.TextField(blank=True)
    join_date = models.DateField()

    def __str__(self):
        return self.username

    def get_all_posts(self):
        return Post.objects.filter(profile=self).order_by('-timestamp') 





class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)

    def __str__(self):
        return f"Post {self.pk} by {self.profile}"

    def get_all_photos(self):
        return Photo.objects.filter(post=self).order_by('timestamp')

    def get_absolute_url(self):
        return reverse('show_post', kwargs={'pk': self.pk})


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to='photos/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url

    def __str__(self):
        return f"Photo for Post {self.post.pk}"


