from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from common.letterboxd import scrape_letterboxd_for_tmdb_id
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


def get_film_data(film: Film):
    if not film.tmdb_id:
        if not film.letterboxd:
            # nothing we can do here
            return
        tmdb_id = scrape_letterboxd_for_tmdb_id(film.letterboxd)
        if not tmdb_id:
            print(f"Cant't get more deatils of {film} because we couldn't find the TMDB id")
            # nothing else we can do here
            return
        film.tmdb_id = tmdb_id
    # if we got here, there is tmdb_id
    if not all(
        [
            film.directors.exists(),
            film.countries.exists(),
            film.genres.exists(),
            film.keywords.exists(),
            film.runtime,
        ]
    ):
        enrich_film_details(film)


class FilmAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "get_directors",
        "year",
        "get_countries",
        "get_genres",
        "runtime",
        "tmdb_id",
        "cc_id",
        "letterboxd_link",
    ]
    list_display_links = ["title"]
    search_fields = ["title", "letterboxd", "tmdb_id"]
    filter_horizontal = ["directors"]
    actions = ["generate_sql_inserts", "get_tmdb_data"]

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

    @admin.action(description="Generate SQL queries")
    def generate_sql_inserts(self, request: HttpRequest, queryset: QuerySet[Film]) -> None:
        queries = []
        for film in queryset:
            sql_query = get_object_sql_insert(film)
            queries.append(sql_query)
            countries_m2m_queries = get_countries_sql_inserts(film)
            queries.extend(countries_m2m_queries)
            directors_m2m_queries = get_directors_sql_inserts(film)
            queries.extend(directors_m2m_queries)

        joined_queries = "<br>".join(queries)
        self.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))

    @admin.action(description="Get TMDB data")
    def get_tmdb_data(self, request: HttpRequest, queryset: QuerySet[Film]) -> None:
        for film in queryset:
            get_film_data(film)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        get_film_data(form.instance)


class FilmSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "film", "venue", "datetime"]
    list_filter = ["venue"]


admin.site.register(Film, FilmAdmin)
admin.site.register(FilmSession, FilmSessionAdmin)
