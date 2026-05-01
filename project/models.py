from django.db import models


class Artist(models.Model):
    name = models.TextField()
    genre = models.TextField()
    origin_country = models.TextField()
    bio = models.TextField()

    def __str__(self):
        return self.name

# music album released by an Artist.Linked to an Artist via a ForeignKey
class Album(models.Model):
    title = models.TextField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    year_released = models.IntegerField()
    genre = models.TextField()
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    external_cover_url = models.URLField(blank=True)
    musicbrainz_release_group_mbid = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"{self.title} ({self.year_released})"

    def external_cover_is_placeholder(self) -> bool:
        """True when ``external_cover_url`` is empty or a generic placeholder, not real art."""
        url = (self.external_cover_url or "").strip().lower()
        if not url:
            return True
        if "placehold.co" in url or "via.placeholder.com" in url:
            return True
        return False
# resloves cover image
    @property
    def display_cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        if self.external_cover_is_placeholder():
            return ""
        return (self.external_cover_url or "").strip()

#a registered user/listener of the application. Listeners can post Reviews and like other Reviews

class Listener(models.Model):
    username = models.CharField(max_length=50, blank=True)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    # cap for profile url input
    profile_image_url = models.URLField(blank=True, max_length=2000)
    bio = models.TextField(blank=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.username:
            return self.username
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_image_src(self) -> str:
        """Stripped URL safe for use in ``<img src>``."""
        return (self.profile_image_url or "").strip()

# a review left by a Listener for an Album or a specific song
class Review(models.Model):
    REVIEW_TARGET_CHOICES = (
        ("album", "Album"),
        ("song", "Song"),
    )

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='reviews')
    listener = models.ForeignKey(Listener, on_delete=models.CASCADE, related_name='reviews')
    review_target = models.CharField(max_length=10, choices=REVIEW_TARGET_CHOICES, default="album")
    track_title = models.CharField(max_length=200, blank=True)
    rating = models.IntegerField()
    review_text = models.TextField()
    date_posted = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.listener} - {self.album} ({self.rating}/10)"

# likes a user can give
class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    listener = models.ForeignKey(Listener, on_delete=models.CASCADE, related_name="liked_reviews")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "listener")

    def __str__(self):
        return f"{self.listener} liked review #{self.review_id}"