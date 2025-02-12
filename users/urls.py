from django.urls import path

from users.views import film_stats, preferences, profile, set_pick_order_criteria, update_time_preferences

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("stats/", film_stats, name="stats"),
    path("preferences/", preferences, name="preferences"),
    path("preferences/pick-criteria/update/", set_pick_order_criteria, name="update-pick-criteria"),
    path("preferences/session-times/update/", update_time_preferences, name="update-session-times"),
]
