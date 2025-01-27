from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from common.models import Country, Gender, Genre, Keyword, Region, Venue
from common.utils import get_object_sql_insert


@admin.action(description="Generate SQL queries")
def generate_sql_inserts(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Country]) -> None:
    queries = []
    for country in Country.objects.all().order_by("pk"):
        sql_query = get_object_sql_insert(country)
        queries.append(sql_query)

    joined_queries = "<br>".join(queries)
    modeladmin.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "get_regions"]
    actions = [generate_sql_inserts]

    @admin.display(description="Regions", ordering="regions__name")
    def get_regions(self, obj: Country):
        return ", ".join([region.name for region in obj.regions.all()])


class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "get_countries"]
    filter_horizontal = ["countries"]

    @admin.display(description="Countries", ordering="countries__name")
    def get_countries(self, obj: Region):
        return ", ".join([country.name for country in obj.countries.all()])


admin.site.register(Country, CountryAdmin)
admin.site.register(Gender)
admin.site.register(Genre)
admin.site.register(Keyword)
admin.site.register(Region, RegionAdmin)
admin.site.register(Venue)
