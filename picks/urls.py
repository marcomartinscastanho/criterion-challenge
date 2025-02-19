from django.urls import path

from picks.views import complete_picks, set_category_pick, toggle_lock

urlpatterns = [
    path("generate/", complete_picks, name="complete_picks"),
    path("set-category-pick/", set_category_pick, name="set-category-pick"),
    path("toggle-lock/", toggle_lock, name="toggle-lock"),
]
