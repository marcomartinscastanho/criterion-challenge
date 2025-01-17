from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from criterionchallenge.utils import get_object_sql_insert
from films.models import Film


@admin.action(description="Generate SQL queries")
def generate_sql_inserts(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Film]) -> None:
    queries = []
    for film in queryset:
        sql_query = get_object_sql_insert(film)
        queries.append(sql_query)

    joined_queries = "<br>".join(queries)
    modeladmin.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


class FilmAdmin(admin.ModelAdmin):
    list_display = ["spine", "title", "get_directors", "country", "year"]
    list_display_links = ["title"]
    search_fields = ["title"]
    filter_horizontal = ["directors"]
    actions = [generate_sql_inserts]

    def get_directors(self, obj: Film):
        return ", ".join([director.name for director in obj.directors.all()])

    get_directors.short_description = "Director"


admin.site.register(Film, FilmAdmin)
