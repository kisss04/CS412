from django.urls import path
from . import views

urlpatterns = [
    # HTML routes
    path('', views.index),
    path('random', views.index),
    path('jokes', views.jokes),
    path('joke/<int:pk>', views.joke_detail),
    path('pictures', views.pictures),
    path('picture/<int:pk>', views.picture_detail),

    # API routes
    path('api/', views.api_random_joke),
    path('api/random', views.api_random_joke),
    path('api/jokes', views.api_all_jokes),
    path('api/joke/<int:pk>', views.api_joke_detail),
    path('api/pictures', views.api_all_pictures),
    path('api/picture/<int:pk>', views.api_picture_detail),
    path('api/random_picture', views.api_random_picture),
]