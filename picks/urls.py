from django.urls import path

from picks.views import picks

urlpatterns = [
    path("picks/", picks, name="picks"),
]
