from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.views import LoginView, register

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
]
