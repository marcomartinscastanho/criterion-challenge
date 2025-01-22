from django.urls import path

from picks.views import picks, update_pick

urlpatterns = [
    path("", picks, name="picks"),
    path("update/<int:pick_id>/", update_pick, name="update_pick"),
]
