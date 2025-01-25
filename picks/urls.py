from django.urls import path

from picks.views import complete_picks, picks, suggestions, update_pick

urlpatterns = [
    path("", picks, name="picks"),
    path("generate/", complete_picks, name="complete_picks"),
    path("update/<int:pick_id>/", update_pick, name="update_pick"),
    path("suggestions/", suggestions, name="suggestions"),
]
