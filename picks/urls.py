from django.urls import path

from picks.views import complete_picks, picks, set_category_pick, toggle_lock, update_pick

urlpatterns = [
    path("", picks, name="picks"),
    path("generate/", complete_picks, name="complete_picks"),
    path("update/<int:pick_id>/", update_pick, name="update_pick"),
    path("set_category_pick/", set_category_pick, name="set_category_pick"),
    path("toggle_lock/", toggle_lock, name="toggle_lock"),
]
