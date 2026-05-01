from django.contrib import admin

from .models import Album, Artist, Listener, Review, ReviewLike


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "genre", "origin_country")
    search_fields = ("name", "genre")


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "year_released", "genre", "musicbrainz_release_group_mbid")
    list_filter = ("year_released", "genre")
    search_fields = ("title", "artist__name")


@admin.register(Listener)
class ListenerAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("album", "listener", "rating", "date_posted")
    list_filter = ("rating", "date_posted")
    search_fields = ("review_text", "album__title", "listener__email")


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ("review", "listener", "created_at")
    search_fields = ("review__album__title", "listener__username", "listener__email")
