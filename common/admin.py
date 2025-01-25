from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from common.models import Country, Venue
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
    actions = [generate_sql_inserts]


admin.site.register(Country, CountryAdmin)
admin.site.register(Venue)
