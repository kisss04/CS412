from django.urls import path
from .views import main, order, confirmation

urlpatterns = [
    path("main/", main, name="main"),
    path("order/", order, name="order"),
    path("confirmation/", confirmation, name="confirmation"),
]
