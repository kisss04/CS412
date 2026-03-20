app_name = "mini_insta"

from django.urls import path
from .views import (
    ProfileDetailView,
    ProfileListView,
    add_post,
    delete_post,
    edit_post,
    edit_profile,
)

urlpatterns = [
    path("", ProfileListView.as_view(), name="profile_list"),

    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="show_profile"),

    path("profile/<int:pk>/edit/", edit_profile, name="edit_profile"),

    path("profile/<int:pk>/add_post/", add_post, name="add_post"),

    path("post/<int:pk>/edit/", edit_post, name="edit_post"),

    path("post/<int:pk>/delete/", delete_post, name="delete_post"),
]