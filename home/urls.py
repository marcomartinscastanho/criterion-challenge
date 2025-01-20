from django.contrib.auth import views as auth_views
from django.urls import path

from home.views import LoginView, home

urlpatterns = [
    path("", home, name="home"),
    path("accounts/login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
