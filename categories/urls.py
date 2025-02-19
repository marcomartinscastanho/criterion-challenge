from django.urls import path

from categories.views import categories, category_detail

urlpatterns = [
    path("", categories, name="categories"),
    path("<int:category_id>/", category_detail, name="category_detail"),
]
