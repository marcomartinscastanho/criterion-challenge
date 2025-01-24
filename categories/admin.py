from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from categories.forms import CategoryForm
from categories.models import Category
from common.constants import CURRENT_YEAR
from common.utils import get_object_sql_insert
from films.models import Film


def get_m2m_sql_inserts(obj: Category, m2m_field_name: str) -> list[str]:
    m2m_field = getattr(obj, m2m_field_name)
    films: QuerySet[Film] = m2m_field.all()
    queries = []
    for film in films.order_by("cc_id"):
        queries.append(
            f"INSERT INTO {Category.films.through._meta.db_table} (category_id, film_id) "
            "SELECT c.id, f.id "
            f"FROM {Category._meta.db_table} c, {Film._meta.db_table} f "
            f"WHERE c.number = {obj.number} AND f.cc_id = {film.cc_id};"
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


class FilmsInline(admin.TabularInline):
    model = Film.categories.through
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        """
        Override the default queryset to include related Film fields.
        """
        queryset = super().get_queryset(request)
        # Prefetch the related Film objects to avoid additional queries
        return queryset.prefetch_related("film")

    def has_add_permission(self, request, obj=...):
        return False

    def has_change_permission(self, request, obj=...):
        return False


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ["number", "title", "num_films"]
    list_display_links = ["title"]
    search_fields = ["title"]
    filter_horizontal = ["films"]
    actions = [generate_sql_inserts]
    inlines = [FilmsInline]

    @admin.display(description="# Films")
    def num_films(self, obj: Category):
        return obj.num_films

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(year=CURRENT_YEAR)


admin.site.register(Category, CategoryAdmin)
