from django.contrib import admin

from .models import Album, Artist, Listener, Review


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "genre", "origin_country")
    search_fields = ("name", "genre")


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "year_released", "genre")
    list_filter = ("year_released", "genre")
    search_fields = ("title", "artist__name")


@admin.register(Listener)
class ListenerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "date_joined")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("album", "listener", "rating", "date_posted")
    list_filter = ("rating", "date_posted")
    search_fields = ("review_text", "album__title", "listener__email")
