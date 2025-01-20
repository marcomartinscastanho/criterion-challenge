from django.urls import path

from categories.views import categories

urlpatterns = [
    path("categories/", categories, name="categories"),
]
