from django.db import models

# Create your models here.
from django.db import models

class Profile(models.Model):
    """
    Represents a user profile in Mini Insta.
    """
    username = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    profile_image_url = models.URLField()
    bio_text = models.TextField(blank=True)
    join_date = models.DateField()

    def __str__(self):
        return self.username