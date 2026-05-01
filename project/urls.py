from django.urls import path

from . import views

app_name = "project"

urlpatterns = [
    path("", views.ProjectHomeView.as_view(), name="home"),
    path("sign-in/", views.sign_in_view, name="sign_in"),
    path("sign-out/", views.sign_out_view, name="sign_out"),
    path("me/", views.my_profile_view, name="my_profile"),
    path("me/delete/", views.delete_my_profile_view, name="my_profile_delete"),
    path("musicbrainz/", views.musicbrainz_lookup_view, name="musicbrainz_lookup"),
    path("artists/", views.ArtistListView.as_view(), name="artist_list"),
    path("artists/<int:pk>/", views.ArtistDetailView.as_view(), name="artist_detail"),
    path("albums/", views.AlbumListView.as_view(), name="album_list"),
    path("albums/<int:pk>/", views.AlbumDetailView.as_view(), name="album_detail"),
    path("listeners/", views.ListenerListView.as_view(), name="listener_list"),
    path("listeners/<int:pk>/", views.ListenerDetailView.as_view(), name="listener_detail"),
    path(
        "listeners/<int:pk>/edit-profile/",
        views.ListenerProfileUpdateView.as_view(),
        name="listener_profile_edit",
    ),
    path("reviews/", views.ReviewListView.as_view(), name="review_list"),
    path("reviews/add/", views.ReviewHubView.as_view(), name="review_hub"),
    path("reviews/add/<int:album_id>/", views.review_compose_view, name="review_compose"),
    path("reviews/<int:pk>/like/", views.toggle_review_like_view, name="review_like"),
    path("reviews/new/", views.ReviewCreateView.as_view(), name="review_create"),
    path("reviews/<int:pk>/edit/", views.ReviewUpdateView.as_view(), name="review_edit"),
    path(
        "reviews/<int:pk>/delete/",
        views.ReviewDeleteView.as_view(),
        name="review_delete",
    ),
]
