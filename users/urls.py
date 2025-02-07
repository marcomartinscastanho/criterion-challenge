from django.urls import path

from users.views import film_stats, preferences, profile, set_pick_order_criteria

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("stats/", film_stats, name="stats"),
    path("preferences/", preferences, name="preferences"),
    path("preferences/pick-criteria/update/", set_pick_order_criteria, name="update_pick_criteria"),
]
