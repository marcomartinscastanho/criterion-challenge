from django.urls import path

from users.views import (
    film_stats,
    preferences,
    profile,
    update_filter_preferences,
    update_pick_order_criteria,
    update_session_times,
)

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("stats/", film_stats, name="stats"),
    path("preferences/", preferences, name="preferences"),
    path("preferences/pick-criteria/update/", update_pick_order_criteria, name="update-pick-order-criteria"),
    path("preferences/session-times/update/", update_session_times, name="update-session-times"),
    path("preferences/filters/update/", update_filter_preferences, name="update-filter-preferences"),
]
