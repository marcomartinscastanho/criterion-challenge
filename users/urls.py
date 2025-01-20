from django.urls import path

from users.views import profile, upload_csv

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("upload_csv/", upload_csv, name="upload_csv"),
]
