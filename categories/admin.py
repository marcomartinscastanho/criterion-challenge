from django.contrib import admin

from categories.forms import CategoryForm
from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ["number", "title", "num_films"]
    list_display_links = ["title"]
    search_fields = ["title"]
    filter_horizontal = ("films",)  # Allows to select multiple films

    def num_films(self, obj: Category):
        return obj.num_films

    num_films.short_description = "# Films"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(year=CURRENT_YEAR)


admin.site.register(Category, CategoryAdmin)
