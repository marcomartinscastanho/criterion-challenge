from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from common.utils import get_object_sql_insert
from directors.models import Director
from directors.utils import enrich_director_details


@admin.action(description="Generate SQL queries")
def generate_sql_inserts(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Director]) -> None:
    queries = []
    for director in Director.objects.all().order_by("pk"):
        sql_query = get_object_sql_insert(director)
        queries.append(sql_query)

    joined_queries = "<br>".join(queries)
    modeladmin.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


@admin.action(description="Get TMDB data")
def get_tmdb_data(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Director]) -> None:
    for director in queryset:
        enrich_director_details(director)


class DirectorAdmin(admin.ModelAdmin):
    list_display = ["name", "tmdb_id", "gender"]
    list_filter = ["gender"]
    actions = [generate_sql_inserts, get_tmdb_data]


admin.site.register(Director, DirectorAdmin)
