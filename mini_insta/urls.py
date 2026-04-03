app_name = "mini_insta"

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import ProfileDetailView, ProfileListView, CreateProfileView

urlpatterns = [

    path("", ProfileListView.as_view(), name="profile_list"),

    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="show_profile"),

    path("profile/", views.my_profile, name="my_profile"),

    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("profile/add_post/", views.add_post, name="add_post"),

    path("post/<int:pk>/edit/", views.edit_post, name="edit_post"),

    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),

    path("profile/<int:pk>/follow/", views.follow_profile, name="follow_profile"),

    path("profile/<int:pk>/delete_follow/", views.delete_follow_profile, name="delete_follow"),

    path("post/<int:pk>/like/", views.like_post, name="like_post"),

    path("post/<int:pk>/delete_like/", views.delete_like_post, name="delete_like"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="mini_insta/login.html"),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="mini_insta:logout_confirmation"),
        name="logout",
    ),

    path(
        "logout_confirmation/",
        views.LogoutConfirmationView.as_view(),
        name="logout_confirmation",
    ),

    path(
        "create_profile/",
        CreateProfileView.as_view(),
        name="create_profile",
    ),
]