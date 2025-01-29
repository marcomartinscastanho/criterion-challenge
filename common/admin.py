from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from common.models import Country, Gender, Genre, Keyword, Region, Venue
from common.utils import get_object_sql_insert


class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "get_regions"]
    actions = ["generate_sql_inserts"]

    @admin.display(description="Regions", ordering="regions__name")
    def get_regions(self, obj: Country):
        return ", ".join([region.name for region in obj.regions.all()])

    @admin.action(description="Generate SQL queries")
    def generate_sql_inserts(self, request: HttpRequest, queryset: QuerySet[Country]) -> None:
        queries = []
        for country in Country.objects.all().order_by("pk"):
            sql_query = get_object_sql_insert(country)
            queries.append(sql_query)

        joined_queries = "<br>".join(queries)
        self.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


class KeywordAdmin(admin.ModelAdmin):
    list_display = ["name", "get_films"]
    search_fields = ["name"]

    @admin.display(description="Films", ordering="films__title")
    def get_films(self, obj: Keyword):
        return ", ".join([film.title for film in obj.films.all()])


class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "get_countries"]
    filter_horizontal = ["countries"]

    @admin.display(description="Countries", ordering="countries__name")
    def get_countries(self, obj: Region):
        return ", ".join([country.name for country in obj.countries.all()])


admin.site.register(Country, CountryAdmin)
admin.site.register(Gender)
admin.site.register(Genre)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Venue)
