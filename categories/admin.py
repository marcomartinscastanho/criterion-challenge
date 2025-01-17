from django.contrib import admin

from categories.constants import CURRENT_YEAR
from categories.forms import CategoryForm
from categories.models import Category


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(year=CURRENT_YEAR)


admin.site.register(Category, CategoryAdmin)
