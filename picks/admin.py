from django.contrib import admin

from criterionchallenge.constants import CURRENT_YEAR
from picks.forms import PickForm
from picks.models import Pick


class PickAdmin(admin.ModelAdmin):
    form = PickForm
    list_display = ["category", "film", "film_year", "watched", "user"]
    list_filter = ["user"]

    def film_year(self, obj: Pick):
        return obj.film.year

    film_year.short_description = "Year"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(year=CURRENT_YEAR)


admin.site.register(Pick, PickAdmin)
