from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from categories.forms import CategoryForm
from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR
from criterionchallenge.utils import get_object_sql_insert
from films.models import Film


def get_m2m_sql_inserts(obj: Category, m2m_field_name: str) -> list[str]:
    """
    Generate SQL INSERT queries for the ManyToMany relationship of the given object.

    Args:
        obj (Model): The model instance with a ManyToMany field.
        m2m_field_name (str): The name of the ManyToMany field.

    Returns:
        list[str]: A list of SQL INSERT queries for the pivot table.
    """
    table = obj._meta.db_table
    m2m_field = getattr(obj, m2m_field_name)
    films: QuerySet[Film] = m2m_field.all()
    pivot_table = m2m_field.through._meta.db_table
    queries = []
    for film in films.order_by("cc_id"):
        queries.append(
            f"INSERT INTO {pivot_table} (category_id, film_id) "
            "SELECT c.id, f.cc_id "
            f"FROM {table} c "
            "JOIN films_film f "
            f"ON f.cc_id = {film.pk} "
            f"WHERE c.year = {CURRENT_YEAR} AND c.number = {obj.number};"
        )
    return queries


@admin.action(description="Generate SQL queries")
def generate_sql_inserts(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Category]) -> None:
    queries = []
    for category in queryset.order_by("number"):
        sql_query = get_object_sql_insert(category)
        queries.append(sql_query)
        m2m_queries = get_m2m_sql_inserts(category, "films")
        queries.extend(m2m_queries)

    joined_queries = "<br>".join(queries)
    modeladmin.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ["number", "title", "num_films"]
    list_display_links = ["title"]
    search_fields = ["title"]
    filter_horizontal = ("films",)  # Allows to select multiple films
    actions = [generate_sql_inserts]

    def num_films(self, obj: Category):
        return obj.num_films

    num_films.short_description = "# Films"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(year=CURRENT_YEAR)


admin.site.register(Category, CategoryAdmin)
