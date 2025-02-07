from django.urls import path

from users.views import profile, set_pick_order_criteria

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("preferences/pick-criteria/update/", set_pick_order_criteria, name="update_pick_criteria"),
]
