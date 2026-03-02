from django.contrib import admin


# Register your models here.

from django.contrib import admin
from .models import Profile, Post, Photo

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)

