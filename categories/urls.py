from django.urls import path

from categories.views import categories, category_detail

urlpatterns = [
    path("categories/", categories, name="categories"),
    path("categories/<int:category_id>/", category_detail, name="category_detail"),
]
