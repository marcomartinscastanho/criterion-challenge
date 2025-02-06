from django.urls import path

from home.views import home, test

urlpatterns = [
    path("", home, name="home"),
    path("test", test, name="test"),  # XXX: remove
]
