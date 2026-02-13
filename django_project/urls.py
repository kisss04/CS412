
#from django.contrib import admin
#from django.urls import path

#urlpatterns = [
#    path("admin/", admin.site.urls),
#]


from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("quotes.urls")),
    path("restaurant/", include("restaurant.urls")),
    path("mini_insta/", include("mini_insta.urls")),
]
