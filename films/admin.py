from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from common.models import Country
from common.utils import get_object_sql_insert
from directors.models import Director
from films.models import Film, FilmSession
from films.utils import enrich_film_details


def get_countries_sql_inserts(film: Film) -> list[str]:
    queries = []
    for country in film.countries.all():
        queries.append(
            f"INSERT INTO films_film_countries (film_id, country_id) "
            "SELECT f.id, c.id "
            f"FROM {Film._meta.db_table} f, {Country._meta.db_table} c "
            f"WHERE f.cc_id = {film.cc_id} AND c.id = {country.pk};"
        )
    return queries


def get_directors_sql_inserts(film: Film) -> list[str]:
    queries = []
    for director in film.directors.all():
        queries.append(
            f"INSERT INTO films_film_directors (film_id, director_id) "
            "SELECT f.id, d.id "
            f"FROM {Film._meta.db_table} f, {Director._meta.db_table} d "
            f"WHERE f.cc_id = {film.cc_id} AND d.id = {director.pk};"
        )
    return queries


@admin.action(description="Generate SQL queries")
def generate_sql_inserts(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Film]) -> None:
    queries = []
    for film in Film.objects.all():
        sql_query = get_object_sql_insert(film)
        queries.append(sql_query)
        countries_m2m_queries = get_countries_sql_inserts(film)
        queries.extend(countries_m2m_queries)
        directors_m2m_queries = get_directors_sql_inserts(film)
        queries.extend(directors_m2m_queries)

    joined_queries = "<br>".join(queries)
    modeladmin.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


@admin.action(description="Get TMDB data")
def get_tmdb_data(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Film]) -> None:
    # TODO: make this async if queryset.count() is large (> 50, e.g.)
    for film in queryset:
        enrich_film_details(film)


class FilmAdmin(admin.ModelAdmin):
    list_display = ["title", "get_directors", "year", "get_countries", "get_genres", "runtime", "letterboxd_link"]
    list_display_links = ["title"]
    search_fields = ["title", "letterboxd"]
    filter_horizontal = ["directors"]
    actions = [generate_sql_inserts, get_tmdb_data]

    # TODO: create a separation in the form for external data (letterboxd url, cc_id, cc spine, tmdb id)

    @admin.display(description="Letterboxd", ordering="letterboxd")
    def letterboxd_link(self, obj: Film):
        return format_html('<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>', url=obj.letterboxd)

    @admin.display(description="Director", ordering="directors__name")
    def get_directors(self, obj: Film):
        return ", ".join([director.name for director in obj.directors.all()])

    @admin.display(description="Country", ordering="countries__name")
    def get_countries(self, obj: Film):
        return ", ".join([country.name for country in obj.countries.all()])

    @admin.display(description="Genres", ordering="genres__name")
    def get_genres(self, obj: Film):
        return ", ".join([genre.name for genre in obj.genres.all()])


admin.site.register(Film, FilmAdmin)
admin.site.register(FilmSession)
