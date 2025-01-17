from django.contrib import admin

from categories.forms import CategoryForm
from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ["number", "title", "year", "get_films"]
    search_fields = ["title", "year"]
    filter_horizontal = ("films",)  # Allows to select multiple films

    def get_films(self, obj):
        return ", ".join([film.title for film in obj.films.all()])

    get_films.short_description = "Films"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(year=CURRENT_YEAR)


admin.site.register(Category, CategoryAdmin)
