from django.db import models

class Artist(models.Model):
    name = models.TextField()
    genre = models.TextField()
    origin_country = models.TextField()
    bio = models.TextField()

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.TextField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    year_released = models.IntegerField()
    genre = models.TextField()
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.year_released})"


class Listener(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Review(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='reviews')
    listener = models.ForeignKey(Listener, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    review_text = models.TextField()
    date_posted = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.listener} - {self.album} ({self.rating}/10)"