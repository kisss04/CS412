
#from django.contrib import admin
#from django.urls import path

#urlpatterns = [
#    path("admin/", admin.site.urls),
#]


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("quotes.urls")),
    path("restaurant/", include("restaurant.urls")),
    path("mini_insta/", include("mini_insta.urls")),
    path("voter_analytics/", include("voter_analytics.urls")),
    path('jokesapp/', include('jokesapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
